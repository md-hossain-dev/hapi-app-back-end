function toggleNav() {
    var sidenav = document.getElementById("mySidenav");
    var icon = document.querySelector(".topnav .icon");
    var content = document.querySelector(".content");

    if (sidenav.style.width === "250px") {
        sidenav.style.width = "0";
        icon.classList.remove("close");
        content.classList.remove("sidenav-open"); // Remove the class
        document.removeEventListener('click', outsideClickListener);
    } else {
        sidenav.style.width = "250px";
        icon.classList.add("close");
        content.classList.add("sidenav-open"); // Add the class
        document.addEventListener('click', outsideClickListener);
    }
}

function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
    document.querySelector(".topnav .icon").classList.remove("close");
    document.querySelector(".content").classList.remove("sidenav-open"); // Remove the class
    document.removeEventListener('click', outsideClickListener);
}

function outsideClickListener(event) {
    var sidenav = document.getElementById("mySidenav");
    var icon = document.querySelector(".topnav .icon");

    if (!sidenav.contains(event.target) && !icon.contains(event.target)) {
        closeNav();
    }
}

// Function to show user notifications
function showNotifications() {
    // Add your logic here to show notifications
}

// Function to toggle user menu dropdown
function toggleUserMenu() {
    var dropdown = document.getElementById("userDropdown");
    if (dropdown.style.display === "block") {
        dropdown.style.display = "none";
    } else {
        dropdown.style.display = "block";
    }
}

// Function to handle logout action
function logout() {
    // Add your logout logic here
}


// Get the modal
var modal = document.getElementById("myModal");

// Get the button that opens the modal
var btn = document.getElementById("openModalBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks the button, open the modal 
btn.onclick = function() {
    modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}