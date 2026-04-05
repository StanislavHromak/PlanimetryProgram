let scale = 1;
let isDragging = false;
let startX, startY, translateX = 0, translateY = 0;

export function openImageModal(src) {
    const modal = document.getElementById('image-modal');
    const img = document.getElementById('modal-image');
    img.src = src;
    modal.style.display = 'flex';

    scale = 1; translateX = 0; translateY = 0;
    img.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
}

export function initModalListeners() {
    document.getElementById('image-modal').addEventListener('click', function(e) {
        if (e.target.id === 'image-modal') {
            this.style.display = 'none';
        }
    });

    document.getElementById('close-modal-btn').addEventListener('click', function() {
        document.getElementById('image-modal').style.display = 'none';
    });

    const zoomContainer = document.getElementById('zoom-container');
    const modalImage = document.getElementById('modal-image');

    zoomContainer.addEventListener('wheel', (e) => {
        e.preventDefault();
        scale += e.deltaY * -0.002;
        scale = Math.min(Math.max(0.5, scale), 10);
        modalImage.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
    });

    zoomContainer.addEventListener('mousedown', (e) => {
        isDragging = true;
        startX = e.clientX - translateX;
        startY = e.clientY - translateY;
        zoomContainer.style.cursor = 'grabbing';
    });

    window.addEventListener('mouseup', () => {
        isDragging = false;
        zoomContainer.style.cursor = 'grab';
    });

    window.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        e.preventDefault();
        translateX = e.clientX - startX;
        translateY = e.clientY - startY;
        modalImage.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
    });
}