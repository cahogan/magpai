import typescript from "@rollup/plugin-typescript"
import glob from "glob"
import * as path from "path"
import * as fs from "fs"

function getHtmlSnippet(jsFilename) {
  const htmlSnippet = `
{% comment %}
This file was generated with 'npm run build'.
{% endcomment %}
{% load static %}
<script src="{% static '${jsFilename}' %}" type="text/javascript"></script>
`
  return htmlSnippet
}

/**
 *
 * @param {*} fileOut - project-name/static/project-name/built/page-name/timestamp.js
 *
 * Plugin to save the HTML snippet <script src="{% static 'project-name/built/page-name/timestamp.js' %}" type="text/javascript"></script>
 * And save it to a reliable location for import with name page-name.html
 *
 * @returns rollup plugin
 */
function createHtmlScriptSnippet(fileOut) {
  return {
    name: 'create-html-script-snippet',
    async generateBundle() {
      let { dir: pageNameBase, base: timestampFilename } = path.parse(fileOut)
      let { dir: builtBase, base: pageName } = path.parse(pageNameBase)
      let { dir: projectNameBase, base: _built } = path.parse(builtBase)
      let { base: projectName } = path.parse(projectNameBase)

      const htmlStaticImportPath = path.join(projectName, 'built', pageName, timestampFilename)
      const htmlSnippet = getHtmlSnippet(htmlStaticImportPath)

      const dirName = path.join(projectName, "templates", projectName, "built")
      const fileName = path.join(dirName, `${pageName}.html`)
      fs.mkdirSync(dirName, { recursive: true });
      fs.writeFileSync(fileName, htmlSnippet)
    }
  }
}

// Find all page.ts files in the project
// Assumes that page.ts files are in a folder namespaced by the page name
// We can filter for a particular page to speed up build times
function getEntryPoints(pageName = undefined) {
  let pageFilter = "**/page.ts"
  if (pageName) {
    console.log(`Building ${pageName}`)
    pageFilter = `**/${pageName}/page.ts`
  }
  const entryPoints = glob.sync(pageFilter).map((file) => {
    const { dir } = path.parse(file)
    const pagesParentDir = path.dirname(dir)
    const pageDir = path.basename(dir)
    const timestamp = Date.now()
    const builtFilePath = path.join(
      pagesParentDir,
      "built",
      pageDir,
      `${timestamp}.js`,
    )
    return [file, builtFilePath]
  })
  return entryPoints
}

const defaultPlugins = [typescript()]

function createConfig(entryPoints) {
  const rollupConfig = entryPoints.map(([inputFilePath, outputFilePath]) => {

    return {
      input: inputFilePath,
      output: {
        file: outputFilePath,
        format: "cjs",
        sourcemap: true,
      },
      plugins: [
        ...defaultPlugins,
        createHtmlScriptSnippet(outputFilePath),
      ],
    }
  })
  return rollupConfig
}

// Users can specify configEntrypointFile to filter page to build
// example: npm run build -- --configEntrypointFile game will build any 'game' pages only
export default commandLineArgs => {
  const entryPoints = getEntryPoints(commandLineArgs.configEntrypointFile)
  return createConfig(entryPoints)
}
