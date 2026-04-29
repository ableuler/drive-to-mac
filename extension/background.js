const HOST_NAME = 'com.cudos.drive_to_mac';

// Create a context menu entry
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "revealInFinder",
    title: "Reveal in Finder",
    contexts: ["all"],
    documentUrlPatterns: ["https://drive.google.com/*"]
  });
});

// Helper to extract File ID from URL
function getFileId(url) {
  if (!url) return null;
  const patterns = [
    /\/file\/d\/([a-zA-Z0-9\-_]+)/,
    /\/folders\/([a-zA-Z0-9\-_]+)/,
    /\/d\/([a-zA-Z0-9\-_]+)/,
    /[?&]id=([a-zA-Z0-9\-_]+)/
  ];
  for (const regex of patterns) {
    const match = url.match(regex);
    if (match && match[1]) return match[1];
  }
  return null;
}

function sendToNativeHost(webId) {
  chrome.runtime.sendNativeMessage(
    HOST_NAME,
    { web_id: webId },
    (response) => {
      if (chrome.runtime.lastError) {
        console.error('Native Messaging Error:', chrome.runtime.lastError.message);
      } else if (response && response.status === 'error') {
        console.error('Host Error:', response.message);
      }
    }
  );
}

// Handle context menu click
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "revealInFinder") {
    // 1. Try URL first
    let webId = getFileId(info.linkUrl) || getFileId(info.pageUrl);
    
    if (webId) {
      sendToNativeHost(webId);
    } else {
      // 2. Ask content script for the right-clicked element ID
      chrome.tabs.sendMessage(tab.id, { action: "getLastClickedId" }, (response) => {
        if (response && response.id) {
          sendToNativeHost(response.id);
        } else {
          alert('Could not find a File ID. Try right-clicking the file name directly.');
        }
      });
    }
  }
});
