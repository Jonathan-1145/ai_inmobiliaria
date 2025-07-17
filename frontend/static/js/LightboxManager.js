export function setupLightbox() {
    const modal = document.getElementById("img-modal");
    const modalImg = document.getElementById("img-modal-content");
    const btnPrev = document.getElementById("img-prev");
    const btnNext = document.getElementById("img-next");

    let currentIndex = 0;
    let currentGroup = [];

    function showModal(index) {
        if (!currentGroup.length) return;
        currentIndex = (index + currentGroup.length) % currentGroup.length;
        modalImg.src = currentGroup[currentIndex].getAttribute("data-full");
        modal.style.display = "flex";
    }

    document.addEventListener("click", function (e) {
        const img = e.target.closest(".zoomable-img");
        if (img) {
            const groupId = img.getAttribute("data-group");
            currentGroup = [...document.querySelectorAll(`.zoomable-img[data-group="${groupId}"]`)];
            currentIndex = currentGroup.indexOf(img);
            showModal(currentIndex);
        } else if (e.target.id === "img-modal") {
            modal.style.display = "none";
            currentGroup = [];
        }
    });

    btnPrev.addEventListener("click", function (e) {
        e.stopPropagation();
        showModal(currentIndex - 1);
    });

    btnNext.addEventListener("click", function (e) {
        e.stopPropagation();
        showModal(currentIndex + 1);
    });
}