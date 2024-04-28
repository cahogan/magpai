function showCameraVideoFeed(videoElement: HTMLVideoElement) {
    const camera = navigator.mediaDevices
    if (camera) {
      camera
        .getUserMedia({
            audio: false,
            video: {
              facingMode: 'user',
            }})
        .then((stream) => {
          videoElement.srcObject = stream
        })
        .catch((err) => {
          console.log(`Error accessing camera: ${err}`)
        })
    } else {
      console.log('No camera found.')
    }
  }

function takePhoto(videoElement: HTMLVideoElement, canvas: HTMLCanvasElement) {
    const context = canvas.getContext('2d')
    if (context) {
      context.drawImage(videoElement, 0, 0, canvas.width, canvas.height)
    }
  }

function showCanvasInsteadOfVideo(videoElement: HTMLVideoElement, canvas: HTMLCanvasElement) {
    canvas.classList.remove('hidden')
    videoElement.classList.add('hidden')
  }

function addImageToForm(imageData: string) {
    const photoInput = document.getElementById('photo-input') as HTMLInputElement
    photoInput.value = imageData
  }

// Connect the video feed to the video element
const videoElement = document.getElementById('camera-feed') as HTMLVideoElement
videoElement.setAttribute('autoplay', '');
videoElement.setAttribute('muted', '');
videoElement.setAttribute('playsinline', '');

if (videoElement) {
  showCameraVideoFeed(videoElement)
}

// Add a "take photo" button that captures and displays the current video frame,
// then adds the photo to the form as a base64-encoded image
const takePhotoButton = document.getElementById('take-photo')
if (takePhotoButton) {
  takePhotoButton.addEventListener('click', () => {
    const canvas = document.getElementById('photo-canvas') as HTMLCanvasElement
    takePhoto(videoElement, canvas)
    showCanvasInsteadOfVideo(videoElement, canvas)
    const photoData = canvas.toDataURL('image/png')
    addImageToForm(photoData)
  })
}
