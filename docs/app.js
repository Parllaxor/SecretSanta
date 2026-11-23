
const loginForm = document.getElementById("login-form");
const message = document.getElementById("message");
const result = document.getElementById("result");
const recipientDisplay = document.getElementById("recipient");

function decodeBase64(value) {
    return Uint8Array.from(atob(value), character =>
        character.charCodeAt(0)
    );
}

async function decryptData(encrypted, password, iterations) {
    const salt = decodeBase64(encrypted.salt);
    const nonce = decodeBase64(encrypted.nonce);
    const ciphertext = decodeBase64(encrypted.data);

    const passwordKey = await crypto.subtle.importKey(
        "raw",
        new TextEncoder().encode(password),
        "PBKDF2",
        false,
        ["deriveKey"]
    );

    const key = await crypto.subtle.deriveKey(
        {
            name: "PBKDF2",
            salt: salt,
            iterations: iterations,
            hash: "SHA-256"
        },
        passwordKey,
        {
            name: "AES-GCM",
            length: 256
        },
        false,
        ["decrypt"]
    );

    const decrypted = await crypto.subtle.decrypt(
        {
            name: "AES-GCM",
            iv: nonce
        },
        key,
        ciphertext
    );

    return JSON.parse(new TextDecoder().decode(decrypted));
}

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    message.textContent = "Checking credentials...";
    result.hidden = true;

    const username = document.getElementById("username").value.trim().toLowerCase();
    const password = document.getElementById("password").value;

    try {
        const response = await fetch("database.json");

        if (!response.ok) {
            throw new Error("Could not load database.");
        }

        const database = await response.json();
        const participant = database.participants[username];

        if (!participant) {
            throw new Error("Invalid credentials.");
        }

        const data = await decryptData(
            participant,
            password,
            database.iterations
        );

        recipientDisplay.textContent = data.recipient;
        result.hidden = false;
        message.textContent = "";

    } catch (error) {
        message.textContent = "Invalid username or password.";
        console.error(error);
    }
});
