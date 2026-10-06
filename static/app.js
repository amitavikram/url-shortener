const input = document.getElementById("inputurl");

const button = document.getElementById("subbutton");

const pasteButton =
    document.getElementById("pasteButton");

const clearButton =
    document.getElementById("clearButton");

const copyButton =
    document.getElementById("copyButton");

const resultBox =
    document.getElementById("resultBox");

const shortLink =
    document.getElementById("shortLink");

const error =
    document.getElementById("error");


// ==========================================
// INITIAL STATE
// ==========================================

resultBox.style.display = "none";


// ==========================================
// PASTE BUTTON
// ==========================================

pasteButton.addEventListener(
    "click",
    async function () {

        try {

            const text =
                await navigator.clipboard.readText();

            input.value = text;

            input.focus();

            error.textContent = "";

        }

        catch (err) {

            showError(
                "Unable to paste. Please allow clipboard access."
            );

        }

    }
);


// ==========================================
// CLEAR BUTTON
// ==========================================

clearButton.addEventListener(
    "click",
    function () {

        input.value = "";

        error.textContent = "";

        resultBox.style.display = "none";

        input.focus();

    }
);


// ==========================================
// SHORTEN URL
// ==========================================

button.addEventListener(
    "click",
    async function () {

        const url =
            input.value.trim();


        // Empty input

        if (url === "") {

            showError(
                "Please enter a URL."
            );

            return;
        }


        // Check URL format

        if (!isValidURL(url)) {

            showError(
                "Please enter a valid URL."
            );

            return;
        }


        // Clear previous error

        error.textContent = "";

        resultBox.style.display = "none";


        // Button loading state

        button.disabled = true;

        button.textContent =
            "Checking website...";


        try {

            const response =
                await fetch(
                    "/shorten",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify({
                                url: url
                            })
                    }
                );


            const data =
                await response.json();


            // Backend error

            if (!response.ok) {

                showError(
                    data.error ||
                    "Unable to shorten URL."
                );

                return;
            }


            // Display shortened URL

            shortLink.href =
                data.short_url;

            shortLink.textContent =
                data.short_url;

            resultBox.style.display =
                "flex";


        }

        catch (err) {

            console.error(err);

            showError(
                "Unable to connect to the server."
            );

        }

        finally {

            button.disabled = false;

            button.textContent =
                "Shorten URL";

        }

    }
);


// ==========================================
// URL FORMAT VALIDATION
// ==========================================

function isValidURL(url) {

    try {

        const parsedURL =
            new URL(url);


        return (
            parsedURL.protocol === "http:" ||
            parsedURL.protocol === "https:"
        );

    }

    catch {

        return false;

    }

}


// ==========================================
// SHOW ERROR
// ==========================================

function showError(message) {

    error.textContent =
        message;

    resultBox.style.display =
        "none";

}


// ==========================================
// COPY SHORT URL
// ==========================================

copyButton.addEventListener(
    "click",
    async function () {

        const url =
            shortLink.href;


        if (
            !url ||
            url === "#"
        ) {

            return;

        }


        try {

            await navigator.clipboard.writeText(
                url
            );


            copyButton.textContent =
                "Copied!";


            setTimeout(
                function () {

                    copyButton.textContent =
                        "Copy";

                },
                1500
            );

        }

        catch {

            showError(
                "Unable to copy the URL."
            );

        }

    }
);