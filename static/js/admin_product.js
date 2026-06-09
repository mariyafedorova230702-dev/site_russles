document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("adminImageFile");
    const preview = document.getElementById("adminImagePreview");
    const fileName = document.getElementById("adminImageFileName");
    let previewUrl = "";

    if (!fileInput || !preview || !fileName) {
        return;
    }

    fileInput.addEventListener("change", () => {
        const file = fileInput.files[0];

        if (previewUrl) {
            URL.revokeObjectURL(previewUrl);
            previewUrl = "";
        }

        if (!file) {
            fileName.textContent = "Файл не выбран";
            return;
        }

        fileName.textContent = file.name;
        previewUrl = URL.createObjectURL(file);
        preview.src = previewUrl;
    });
});
