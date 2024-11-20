// Function to refresh token
const refreshToken = () => {
    const tokenRefresh = { refresh: localStorage.getItem("refreshToken") };
    const postBody = JSON.stringify(tokenRefresh);

    fetch(`http://127.0.0.1:8000/token/refresh/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: postBody,
    })
    .then((response) => response.json())
    .then((data) => {
        if (!data.access) {
            // Handle case when access token is not received (e.g., logout user)
            localStorage.clear();
            window.location.replace(`http://127.0.0.1:8000/logout?next=${window.location.pathname}${window.location.search}`);
        } else {
            // Update access token in local storage
            localStorage.setItem("jwtToken", data.access);
        }
    })
    .catch((error) => {
        console.error('Error refreshing token:', error);
        // Handle error (e.g., logout user)
        localStorage.clear();
        window.location.replace(`http://127.0.0.1:8000/logout?next=${window.location.pathname}${window.location.search}`);
    });
};

// Function to call refreshToken function at regular intervals
const startTokenRefresh = () => {
    // Call refreshToken function initially
    refreshToken();
    
    // Set interval to call refreshToken function every 60 seconds
    const intervalId = setInterval(refreshToken, 60000); // 60 seconds in milliseconds

    // Optionally, clear interval if needed (e.g., when user logs out)
    // clearInterval(intervalId);
};

// Start token refresh
startTokenRefresh();
