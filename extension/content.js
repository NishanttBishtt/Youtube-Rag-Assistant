console.log("Content script loaded")
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {

    if (request.action === "seek") {

        const video = document.querySelector("video");

        if (video) {
            video.currentTime = request.seconds;
            video.play();
        }

    }

});