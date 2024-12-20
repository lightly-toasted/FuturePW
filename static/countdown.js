const hash = document.getElementById('hash').textContent;
let remainingTime = Math.round((new Date(JSON.parse(localStorage.getItem(hash))?.time) - new Date()) / 1000)
|| parseInt(document.querySelector('meta[http-equiv="refresh"]').content);
const countdownElement = document.getElementById('countdown');
const scrollDiv = document.getElementById('scroll');
const contentDiv = document.getElementById('content');
const display = (remainingTime) => {
    const hours = Math.floor(remainingTime / 3600);
    const minutes = Math.floor((remainingTime % 3600) / 60);
    const seconds = remainingTime % 60;
    countdownElement.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
};
display(remainingTime);
const intervalId = setInterval(() => {
    remainingTime -= 1;
    if (remainingTime <= 0) {
        clearInterval(intervalId);
    }
    display(remainingTime);
}, 1000);

window.addEventListener('scroll', () => {
    scrollDiv.style.opacity = Math.max(1 - window.scrollY / contentDiv.clientHeight * 2, 0);
})

document.getElementById('link').addEventListener('click', () => {
    const link = document.getElementById('link').firstElementChild;
    const range = document.createRange();
    range.selectNode(link);
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(range);
    document.execCommand('copy');
});

localStorage.setItem(hash, JSON.stringify({
    data: new URLSearchParams(window.location.search).get('data'),
    time: document.querySelector('meta[name="unlockAt"]').content.replace(/^(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z$/, '$1-$2-$3T$4:$5:$6Z')
}));

let installPrompt = null;
const installButton = document.getElementById('pwa');
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    installPrompt = e;
    installButton.style.display = 'block';
})

installButton.addEventListener('click', (e) => {
    e.preventDefault();
    if (installPrompt) installPrompt.prompt();
})

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
    });
}