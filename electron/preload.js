const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // App information
  getAppVersion: () => ipcRenderer.invoke('app-version'),
  
  // File operations
  showSaveDialog: (options) => ipcRenderer.invoke('show-save-dialog', options),
  showOpenDialog: (options) => ipcRenderer.invoke('show-open-dialog', options),
  
  // Window operations
  minimize: () => ipcRenderer.send('window-minimize'),
  maximize: () => ipcRenderer.send('window-maximize'),
  close: () => ipcRenderer.send('window-close'),
  
  // App events
  onShowPreferences: (callback) => {
    ipcRenderer.on('show-preferences', callback);
    return () => ipcRenderer.removeAllListeners('show-preferences');
  },
  
  // Notifications
  showNotification: (title, body) => {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, { body });
    }
  },
  
  // System information
  platform: process.platform,
  
  // Development helpers
  isDev: process.env.NODE_ENV === 'development'
});

// Security: Remove dangerous globals in production
if (process.env.NODE_ENV === 'production') {
  delete window.require;
  delete window.exports;
  delete window.module;
}