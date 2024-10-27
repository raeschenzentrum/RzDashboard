// create_keyfiles.js

async function submitCreateKeyfilesForm(event) {
    event.preventDefault();
    const form = document.getElementById('keyfileForm');
    const formData = new FormData(form);

    try {
        const response = await fetch('/create_keyfiles', {
            method: 'POST',
            body: formData,
        });

        const resultContainer = document.getElementById('create-keyfiles-result');

        if (response.ok) {
            const html = await response.text();
            resultContainer.innerHTML = html;
        } else {
            resultContainer.innerHTML = "Keyfile creation failed.";
        }
    } catch (error) {
        console.error("Error during form submission:", error);
    }
}
