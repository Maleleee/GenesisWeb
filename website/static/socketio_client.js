// Connect to Socket.IO
const socket = io();

// Update recent logins table in real-time
socket.on('update_recent_logins', (loginEvents) => {
  const recentLoginsBody = document.querySelector('.recent-logins tbody');
  recentLoginsBody.innerHTML = ''; // Clear current logins

  loginEvents.forEach(event => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${event.timestamp}</td>
      <td>${event.email}</td>
      <td>${event.username}</td>
    `;
    recentLoginsBody.appendChild(row);
  });
});