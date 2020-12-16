import 'regenerator-runtime/runtime'

window.onload = function () {
    const submitButton = document.getElementById('submit');
    submitButton.addEventListener('click', async function () {
        const id = document.getElementById('input').value.slice(29);
        window.location.href = `http://localhost:1234/video.html?video_id=${id}`;
    });
}