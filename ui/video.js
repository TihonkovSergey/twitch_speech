import 'regenerator-runtime/runtime'

const promiseTimer = (time) => new Promise(resolve => setTimeout(resolve, time));

// https://www.twitch.tv/videos/827901857

const createDivForLi = (innerText) => {
    const div = document.createElement("div");
    div.innerText = innerText;
    return div;
}

const formatTime = (time) => {
    const formattedTime = (time >= 10) ? time : `0${time}`;
    return formattedTime;
}

const getTimeString = (timeInSeconds) => {
    const hours = Math.trunc(timeInSeconds / 3600);
    const formattedHours = formatTime(hours);
    const seconds = timeInSeconds % 60;
    const formattedSeconds = formatTime(seconds);
    const minutes = Math.trunc(timeInSeconds % 3600 / 60);
    const formattedMinutes = formatTime(minutes);
    return `${formattedHours}:${formattedMinutes}:${formattedSeconds}`;
}

window.onload = async function () {
    console.log('AAAA');
    const back = document.getElementById("back");
    back.addEventListener('click', function () {
        window.location.href = `http://localhost:1234/index.html`;
    });
    let params = (new URL(document.location)).searchParams;
    let videoId = params.get("video_id");
    const url = `http://localhost:5000/?video_id=${videoId}`;
    let data = {
        'status': 'loading..'
    }
    // const videoContainer = document.querySelector(".video-container");
    let status = document.getElementById("status");
    let progress = document.getElementById("progress");
    let downloadSpeed = document.getElementById("download-speed");
    console.log(status);
    while (data.status !== "success" && data.status !== "finished") {
        let response = await fetch(url);
        if (response.ok) {
            data = await response.json();
            status.innerText = data.status;
            progress.innerText = `${data.progress}%`;
            downloadSpeed.innerText = data.download_speed + "/s";
            if (data.status === 'success' || data.status === 'finished') {
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
            ul.innerHTML = '';
            data = await response.json();
            Object.values(data).forEach((obj) => {
                const li = document.createElement('li');
                li.className = "list-item";
                const timeString = getTimeString(obj.timecode);
                const timecode = createDivForLi(timeString);
                timecode.className = "timecode";
                const text = createDivForLi(obj.text);
                li.append(timecode);
                li.append(text);
                ul.append(li);
                timecode.addEventListener('click', () => {
                    player.seek(obj.timecode);
                });
            });
        }
    });
}