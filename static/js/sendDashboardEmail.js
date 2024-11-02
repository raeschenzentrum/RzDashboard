function sendDashboardEmail(boardname2) {
    // Wert von `data-boardname` abrufen
    //const boardname = button.getAttribute("data-boardname");
    
    const recipientEmail = "sven.raesch@teradata.com";
    const subject = "Dashboard PDF";
    const body = "Hier ist dein Dashboard";
    const boardname = "OPS-Shift(Early)";
    const encodedBoardname = encodeURIComponent(boardname); 
    console.log(boardname2);
    const url = `/sendmail_dashboard?tab=${encodedBoardname}&recipient_email=${encodeURIComponent(recipientEmail)}&subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error("Fehler beim Abrufen der URL");
            }
            return response.json();
        })
        .then(data => {
            if (data.message) {
                alert(data.message); // Erfolgsnachricht anzeigen
            } else {
                alert("Das Dashboard konnte nicht gesendet werden.");
            }
        })
        .catch(error => {
            console.error("Fehler:", error);
            alert("Es ist ein Fehler beim Senden aufgetreten.");
        });
}
