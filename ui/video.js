import 'regenerator-runtime/runtime'

const promiseTimer = (time) => new Promise(resolve => setTimeout(resolve, time));

// https://www.twitch.tv/videos/827901857

const createDivForLi = (innerText) => {
    const div = document.createElement("div");
    div.innerText = innerText;
    return div;
}

const getSeconds = (timecode) => {
    const time = timecode.split(':');
    let summaryTime = 0;
    let mult = 1;
    for (let i = time.length - 1; i >= 0; i--) {
        summaryTime += parseFloat(time[i]) * mult;
        mult *= 60;
    }
    return summaryTime;
}

window.onload = async function () {
    let params = (new URL(document.location)).searchParams;
    let videoId = params.get("video_id");
    const url = `http://localhost:5000/?video_id=${videoId}`;
    let data = {
        'status': 'loading..'
    }
    // const videoContainer = document.querySelector(".video-container");
    let status = document.getElementById("status");
    while (data.status !== "success") {
        let response = await fetch(url);
        if (response.ok) {
            data = await response.json();
            status.innerText = data.status;
            if (data.status === 'success') {
                break;
            }
        }
        await promiseTimer(3000);
    }
    document.querySelector(".status").style.display = "none";
    const player = new Twitch.Player("twitch-embed", {
        width: 900,
        height: 600,
        video: videoId,
        autoplay: true
    });
    const submitButton = document.getElementById("submit");
    submitButton.addEventListener('click', async function () {
        const ul = document.querySelector(".context-list");
        const inputText = document.getElementById("input").value;
        const url = `http://localhost:5000/search?video_id=${videoId}&input_text=${inputText}`;
        let response = await fetch(url);
        if (response.ok) {
            data = await response.json();
            Object.values(data).forEach((obj) => {
                const li = document.createElement('li');
                li.className = "list-item";
                const timecode = createDivForLi(obj.timecode);
                timecode.className = "timecode";
                const text = createDivForLi(obj.text);
                li.append(timecode);
                li.append(text);
                ul.append(li);
                timecode.addEventListener('click', () => {
                    player.seek(getSeconds(obj.timecode));
                });
            });
        }
    });
}