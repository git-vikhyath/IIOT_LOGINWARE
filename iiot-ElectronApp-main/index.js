const { app, BrowserWindow } = require('electron')
const nativeImage = require('electron').nativeImage;
var image = nativeImage.createFromPath(__dirname + '/public/images/logo.jpg'); 
// where public folder on the root dir
image.setTemplateImage(true);


function createWindow () {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    icon:image,
    kiosk:true,
    alwaysOnTop:true,
    backgroundColor:"#eceff1",
    frame: false ,
    webPreferences: {
      nodeIntegration: true
    }
  })

win.loadURL('http://127.0.0.1:4200')
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})
