// This script captures the last element that was right-clicked
let lastRightClickedId = null;

document.addEventListener('contextmenu', (event) => {
  // Traverse up the DOM to find the parent element with a data-id
  let target = event.target;
  while (target && target !== document) {
    const id = target.getAttribute('data-id');
    if (id) {
      lastRightClickedId = id;
      break;
    }
    target = target.parentElement;
  }
}, true);

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getLastClickedId") {
    sendResponse({ id: lastRightClickedId });
  }
  return true;
});
