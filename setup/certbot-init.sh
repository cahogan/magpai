!/bin/bash

####################################################################################################
# Credit to @CoolNamesAllTaken for the original script.
# Initializes LetsEncrypt certificates that will be served by Nginx and renewed by Certbot.
#   bash scripts/certbot_init.bash          Runs for real (do this on the web server with HTTP enabled).
#   bash scripts/certbot_init.bash dummy    Do this to override the dummy configuration in .env.prod
#                                           and force generation of dummy certificates.
#   bash scripts/certbot_init.bash staging  Run certbot with --test-certs option to test without hitting
#                                           request limit.
####################################################################################################

# Load variables.
source $(dirname "$0")/../.env.prod
data_path=$(dirname "$0")/../certbot/data # Set this to the certbot folder to dump all the generated stuff into.
docker_compose_path=$(dirname "$0")/../compose.prod.yml

if ! docker compose -f "$docker_compose_path" ps | grep -q "Up"; then
	echo "Docker compose project $docker_compose_path must be running for this script to work properly! Exiting."
	exit 1
fi
# Make sure this script is run as root to avoid issues with removing certificates.
if [ "$(id -u)" -ne 0 ]; then
    echo 'This script must be run by root, exiting.' >&2
    exit 1
fi

# Function to display usage information
usage() {
	echo "Usage: $0 [--dummy] [--staging] [-d <domain>]" 1>&2 
	echo -e "\t--dummy          Create dummy certificates and don't request any challenges."
	echo -e "\t--staging        Run certbot with --test-certs option to test without hitting request limit."
	echo -e "\t-d <domain>		Run certbot for a single domain only."
	exit 1
}

# Parse command line options
while getopts "d:h-:" opt; do
	case "$opt" in
		-)
			case "${OPTARG}" in
				dummy)
					echo "Overriding .env to create dummy certificates only."
					SSL_DUMMY_CERTS_ONLY=1
					;;
				staging)
					echo "Overriding .env to run certbot with --test-only flag."
					SSL_STAGING=1
					;;
				help)
					usage
					;;
				*)
					echo "Invalid string option $OPTARG." >&2
			esac
			;;
		d)
            echo "Running for single domain: $OPTARG"
            DOMAINS=( "${OPTARG}" )
            ;;
		h)
			usage
			;;
		:)
			echo "Option requires an argument" >&2
			usage
			;;
		?)
			echo "Invalid character option." 1>&2
			usage
			;;
		
	esac
done
shift $((OPTIND -1))

if [ ! -e "$data_path/conf/options-ssl-nginx.conf" ] || [ ! -e "$data_path/conf/ssl-dhparams.pem" ]; then
	echo "### Downloading recommended TLS parameters ..."
	mkdir -p "$data_path/conf"
	curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$data_path/conf/options-ssl-nginx.conf"
	curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$data_path/conf/ssl-dhparams.pem"
	echo
fi

# Create all the dummy certificates together, at the same time, to stop NGINX crashing out because it's missing a set of dummy certificates.
dummy_domains=()
for domain in "${DOMAINS[@]}"; do
	domain_folder_path=$data_path/conf/live/$domain

	if [ -d "$domain_folder_path" ]; then
		read -p "Existing data found for $domain. Continue dummy certificate creation and replace existing certificate? (y/N) " decision
		if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
			continue
		else
			echo -e "\tRemoving existing files in $domain_folder_path."
			rm -rf $domain_folder_path
			rm -rf $data_path/conf/archive/$domain
			rm $data_path/conf/renewal/$domain.conf
		fi
	fi

# Do the start Nginx - delete dummy certs - get real certs for domains one by one.
# Only get certs for domains that have had dummy certs generated.
for domain in "${dummy_domains[@]}"; do
	domain_folder_path=$data_path/conf/live/$domain

	if [ -d "$domain_folder_path" ]; then
		read -p "Existing data found for $domain. Continue certificate request and replace existing certificate? (y/N) " decision
		if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
			continue
		fi
	fi

	echo "### Requesting certificate for $domain ..."

	# Nginx gets started after the creation of dummy certs, so that it can be happily fooled by the presence of certificates on startup (dies if it can't find them).
	echo "### Starting nginx ..."
	docker compose -f $docker_compose_path up --force-recreate -d nginx
	echo

	# Nginx has been fooled, now switch out the dummy certs for real ones.
	echo "### Deleting dummy certificate for $domain ..."
	docker compose -f $docker_compose_path run --rm --entrypoint "\
		rm -Rf /etc/letsencrypt/live/$domain && \
		rm -Rf /etc/letsencrypt/archive/$domain && \
		rm -Rf /etc/letsencrypt/renewal/$domain.conf" certbot \
		-v
	echo

	domain_args=" -d $domain"


echo "### Reloading nginx after requesting certificates ..."
docker compose -f $docker_compose_path exec nginx nginx -s reload