const paper = document.getElementById('paper');
const controls = document.getElementById('controls');
const submit = document.getElementById('submit');
const durationSwitch = document.getElementById('durationSwitch');
const durationSwitchText = document.getElementById('durationSwitchText');
const timeNumber = document.getElementById('timeNumber');
const timeUnit = document.getElementById('timeUnit');
const timeLabel = document.getElementById('timeLabel');
let isDuration = true;

document.querySelector('form').addEventListener('submit', async function(e) {
    e.preventDefault();

    submit.disabled = true;
    controls.style.transform = "translateY(200%)";
    controls.style.opacity = "0";
    paper.style.pointerEvents = "none";
    controls.style.pointerEvents = "none";
    
    for (const child of paper.children) {
        child.style.opacity = "0";
    }
    for (const child of paper.children) {
        child.style.opacity = "0";
    }
    
    await new Promise(resolve => setTimeout(resolve, 500));

    if (window.matchMedia("(max-width: 767px)").matches) {
        paper.style.filter = "none";
    }
    paper.style.backgroundColor = "transparent";
    paper.style.backgroundImage = "url('/send.gif')";
    
    await new Promise(resolve => setTimeout(resolve, 800));

    paper.style.transform = `translate(200%, -200%)`;

    await new Promise(resolve => setTimeout(resolve, 1100));

    const formData = new FormData(this);
    if (!isDuration) {
        const date = new Date();
        const selectedDate = new Date(formData.get('timeNumber'));
        const minutes = (selectedDate.getTime() - date.getTime()) / 60000;
        formData.set('timeNumber', String(minutes));
        formData.set('timeUnit', 'minutes');
    }

    const response = await fetch('/', {
        method: 'POST',
        body: formData,
    });
    
    if (response.redirected) {
        window.location.href = response.url;
    }
});

durationSwitchText.style.display = "inline-block";
durationSwitch.addEventListener('click', () => {
    if (isDuration) {
        timeLabel.textContent = "Deliver on";
        durationSwitch.textContent = "duration"
        timeNumber.type = "datetime-local";
        timeNumber.style.width = "20ch";
        timeNumber.style.maxWidth = "80vw";
        timeNumber.min = new Date().toISOString().slice(0, 16);
        timeUnit.style.display = "none";
    } else {
        timeLabel.textContent = "Deliver in";
        durationSwitch.textContent = "date"
        timeNumber.type = "number";
        timeNumber.style.width = "5.5em";
        timeNumber.style.maxWidth = "40vw";
        timeNumber.value = "1";
        timeNumber.min = "1";
        timeUnit.style.display = "inline-block";
    }
    isDuration = !isDuration;
});

const papers = { ...localStorage };
const recentDiv = document.getElementById('recent');
let alertShown = false;
console.log(papers);
for (const [hash, data] of Object.entries(papers)) {
    try {
        const parsed = JSON.parse(data);
        let remainingTime = Math.max(0, Math.round((new Date(parsed.time) - new Date()) / 1000));
        console.log(remainingTime)
        const paper = document.createElement('a')
        paper.classList.add('recent-paper');
        paper.style.transform = `translate(${Math.random() * 20 - 10}px, ${Math.random() * 50 - 20}px)`;
        paper.href = `/unlock?data=${parsed.data}`;
        paper.innerHTML = `
            <img src="/flying.gif" />
            <p>${hash}</p>
        `;
        const countdown = document.createElement('span');
        paper.appendChild(countdown);
        recentDiv.appendChild(paper);

        paper.addEventListener('click', (e) => {
            e.preventDefault();
            if (!alertShown) {
                alertShown = true
                alert("Right-click (long press on mobile) to go to the link, and double click to delete this from your recent list.")
            } 
        });
        paper.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            window.location.href = `/unlock?data=${parsed.data}`;
        });
        paper.addEventListener('dblclick', (e) => {
            e.preventDefault();
            countdown.style.opacity = "0";
            localStorage.removeItem(hash);
            paper.style.display = "absolute";
            paper.style.transform = `rotate(-70deg) translate(20vw, 10vh)`;
            setTimeout(() => {
                recentDiv.removeChild(paper);
            }, 2000);
        });

        const display = (remainingTime) => {
            const hours = Math.floor(remainingTime / 3600);
            const minutes = Math.floor((remainingTime % 3600) / 60);
            const seconds = remainingTime % 60;
            countdown.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        };
        display(remainingTime);
        const intervalId = setInterval(() => {
            if (remainingTime <= 0) {
                paper.classList.add('arrived');
                return clearInterval(intervalId);
            }
            remainingTime -= 1;
            display(remainingTime);
        }, 1000);
    } catch (error) {
        console.error(error);
    }
}

const image = new Image();
image.src = '/send.gif';