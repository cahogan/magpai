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

