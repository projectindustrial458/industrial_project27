document.addEventListener('DOMContentLoaded', () => {
    console.log('KSRTC Dashboard Initialized');

    // Update live time
    function updateTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', { hour12: false });
        const timeElement = document.getElementById('current-time');
        if (timeElement) {
            timeElement.textContent = timeString;
        }
    }

    setInterval(updateTime, 1000);
    updateTime();

    // Initialize EPKM Chart
    const ctx = document.getElementById('epkmChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
                datasets: [{
                    label: 'EPKM Trend',
                    data: [42, 44, 30, 41, 43], // Matches the visual dip in Wed
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.05)',
                    borderWidth: 3,
                    pointBackgroundColor: '#ffffff',
                    pointBorderColor: '#0d6efd',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#e9ecef',
                            borderDash: [5, 5]
                        },
                        ticks: {
                            callback: function (value) {
                                return '₹' + value;
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // Default Date Inputs to Today
    const today = new Date().toISOString().split('T')[0];
    const searchDateInput = document.getElementById('searchDate');
    if (searchDateInput) searchDateInput.value = today;

    // Update Master Log Date Label
    const masterLogDate = document.getElementById('masterLogDate');
    if (masterLogDate) {
        const dateOptions = { weekday: 'long', year: 'numeric', month: 'short', day: 'numeric' };
        masterLogDate.textContent = new Date().toLocaleDateString('en-US', dateOptions);
    }

    // Search Form Logic
    const searchForm = document.getElementById('searchForm');
    const searchResults = document.getElementById('searchResults');

    if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            // Simulate loading or filtering
            const btn = searchForm.querySelector('button');
            const originalText = btn.innerHTML;

            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Searching...';
            btn.disabled = true;

            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
                if (searchResults) {
                    searchResults.classList.remove('d-none');
                }
            }, 800);
        });
    }

    // Authentication Logic
    const AUTH_KEY = 'ksrtc_sm_session';

    function checkAuth() {
        const session = sessionStorage.getItem(AUTH_KEY);
        const isLoginPage = window.location.pathname.includes('login.html');

        if (!session && !isLoginPage) {
            window.location.href = 'login.html';
        } else if (session && isLoginPage) {
            window.location.href = 'index.html';
        }

        // Update Depot Display if on index page
        if (session && !isLoginPage) {
            const data = JSON.parse(session);
            const depotDisplay = document.getElementById('depot-display');
            if (depotDisplay && data.depotId) {
                // Map codes to names (simple mapping for demo)
                const depotNames = {
                    'TVM': 'Thiruvananthapuram Central',
                    'KML': 'Kumily',
                    'ALP': 'Alappuzha',
                    'KTYM': 'Kottayam',
                    'ERS': 'Ernakulam',
                    'TSR': 'Thrissur',
                    'PGT': 'Palakkad',
                    'KKD': 'Kozhikode',
                    'KNR': 'Kannur',
                    'KGD': 'Kasaragod',
                    'OTHER': 'Other Depot'
                };
                const name = depotNames[data.depotId] || data.depotId;
                depotDisplay.textContent = `Depot: ${name} (${data.stationMasterId})`;
            }
        }
    }

    // Run basic auth check on load
    if (!window.location.pathname.includes('login.html')) {
        checkAuth();
    }

    // Logout Handler
    window.logout = function () {
        sessionStorage.removeItem(AUTH_KEY);
        window.location.href = 'login.html';
    };

    // Attach logout to any logout buttons if they exist
    document.addEventListener('click', (e) => {
        const logoutBtn = e.target.closest('#logoutBtn');
        if (logoutBtn) {
            e.preventDefault();
            logout();
        }
    });
    // Live Sequence Tracker Search
    const liveTrackerSearchInput = document.getElementById('liveTrackerSearchInput');
    if (liveTrackerSearchInput) {
        liveTrackerSearchInput.addEventListener('keyup', function () {
            const filter = this.value.toUpperCase();
            const table = document.getElementById('liveTrackerTable');
            const tr = table.getElementsByTagName('tr');

            for (let i = 1; i < tr.length; i++) { // Start from 1 to skip header
                let displayed = false;
                // Search in Bus Number (index 0) and Current Depo (index 8)
                const tdBusNo = tr[i].getElementsByTagName('td')[0];
                const tdDepo = tr[i].getElementsByTagName('td')[8];

                if (tdBusNo || tdDepo) {
                    const txtBusNo = tdBusNo.textContent || tdBusNo.innerText;
                    const txtDepo = tdDepo ? (tdDepo.textContent || tdDepo.innerText) : "";

                    if (txtBusNo.toUpperCase().indexOf(filter) > -1 || txtDepo.toUpperCase().indexOf(filter) > -1) {
                        tr[i].style.display = "";
                    } else {
                        tr[i].style.display = "none";
                    }
                }
            }
        });
    }

    // Initialize Dashboard Updates
    updateDashboard();

    // Auto-refresh every 10 seconds
    setInterval(() => {
        console.log('DEBUG: Auto-refreshing dashboard...');
        updateDashboard();
    }, 10000);
});

// Login Handler
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const depotId = document.getElementById('depotId').value;
        const stationMasterId = document.getElementById('stationMasterId').value;
        const password = document.getElementById('password').value;

        if (depotId && stationMasterId && password) {
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        depotId,
                        stationMasterId,
                        password
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    sessionStorage.setItem('ksrtc_sm_session', JSON.stringify({
                        depotId: depotId,
                        stationMasterId: stationMasterId,
                        loginTime: new Date().toISOString()
                    }));

                    const btn = loginForm.querySelector('button[type="submit"]');
                    btn.innerHTML = '<i class="bi bi-check-circle me-2"></i>Success!';
                    btn.classList.remove('btn-primary');
                    btn.classList.add('btn-success');

                    setTimeout(() => {
                        window.location.href = '/index.html';
                    }, 500);
                } else {
                    alert(data.message || 'Login failed');
                }
            } catch (error) {
                console.error('Error logging in:', error);
                alert('An error occurred during login: ' + error.message);
            }
        }
    });
}

// Waybill Form Handler
const waybillForm = document.getElementById('waybillForm');
if (waybillForm) {
    // Update actual time input live
    function updateActualTime() {
        const now = new Date();
        const HH = String(now.getHours()).padStart(2, '0');
        const mm = String(now.getMinutes()).padStart(2, '0');
        const timeString = `${HH}:${mm}`;
        const actualTimeInput = document.getElementById('actualTime');
        if (actualTimeInput) {
            actualTimeInput.value = timeString;
        }
    }

    updateActualTime();

    waybillForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(waybillForm);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });

        const movementType = document.querySelector('input[name="movementType"]:checked')?.value;
        if (movementType) data.movementType = movementType;

        const btn = waybillForm.querySelector('button[type="submit"]');
        const originalText = btn.innerHTML;

        try {
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Logging...';
            btn.disabled = true;

            const response = await fetch('/api/waybill', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                alert('Waybill entry logged successfully!');
                waybillForm.reset();
                updateActualTime(); // Reset time to now

                // Trigger live update
                if (typeof updateDashboard === 'function') {
                    console.log('DEBUG: Triggering immediate update');
                    updateDashboard();
                }
            } else {
                alert('Error: ' + result.message);
            }
        } catch (error) {
            console.error('Error submitting waybill:', error);
            alert('An error occurred while logging the waybill: ' + error.message);
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    });
}

// Live Dashboard Update Logic
async function updateDashboard() {
    console.log('DEBUG: updateDashboard() started');
    try {
        const response = await fetch('/api/live-data');
        console.log('DEBUG: /api/live-data response status:', response.status);

        if (!response.ok) {
            console.error('DEBUG: Failed to fetch live data');
            return;
        }

        const data = await response.json();
        console.log('DEBUG: Fetched data:', data);

        if (data.status === 'success') {
            // Update Stats
            const activeFleetEl = document.getElementById('activeFleetCount');
            const punctualityEl = document.getElementById('punctualityScore');
            const utilizationEl = document.getElementById('utilizationIndex');

            if (activeFleetEl) {
                activeFleetEl.textContent = data.stats.active_fleet;
            }
            if (punctualityEl) punctualityEl.textContent = data.stats.punctuality + '%';
            if (utilizationEl) utilizationEl.textContent = data.stats.utilization + '%';

            // Update Table
            const tableBody = document.querySelector('#liveTrackerTable tbody');
            if (tableBody) {
                console.log('DEBUG: Updating table with', data.waybills.length, 'rows');
                tableBody.innerHTML = ''; // Clear current rows

                if (data.waybills.length === 0) {
                    tableBody.innerHTML = '<tr><td colspan="10" class="text-center py-4 text-muted">No live data available for this depot yet.</td></tr>';
                } else {
                    data.waybills.forEach(wb => {
                        const tr = document.createElement('tr');

                        // Movement Check
                        let schArr = '-', actArr = '-', schDep = '-', actDep = '-';
                        let badgeClass = '';

                        // Basic Logic for times
                        if (wb.movementType === 'Arrival') {
                            schArr = wb.scheduledTime;
                            actArr = wb.actualTime;
                            badgeClass = 'bg-success-subtle text-success';
                        } else {
                            schDep = wb.scheduledTime;
                            actDep = wb.actualTime;
                            badgeClass = 'bg-warning-subtle text-warning';
                        }

                        // Delay Calculation Logic
                        let isDelayed = false;
                        if (wb.actualTime > wb.scheduledTime) {
                            isDelayed = true;
                        }

                        // Helper for class
                        const timeClass = isDelayed ? 'text-danger' : 'text-success';
                        const deviationText = isDelayed ? 'Delayed' : 'On Time';
                        const deviationClass = isDelayed ? 'text-danger fw-bold' : 'text-success fw-bold';

                        tr.innerHTML = `
                            <td class="ps-4 fw-bold">${wb.busRegNo}</td>
                            <td><span class="badge border text-dark rounded-pill fw-normal px-3">${wb.serviceCategory}</span></td>
                            <td>${wb.origin} - ${wb.destination}</td>
                            
                            <td>${schArr}</td>
                            <td class="${wb.movementType === 'Arrival' ? timeClass : ''}">${actArr}</td>
                            <td>${schDep}</td>
                            <td class="${wb.movementType === 'Departure' ? timeClass : ''}">${actDep}</td>
                            
                            <td class="${deviationClass}">${deviationText}</td>
                            <td>${wb.depot_id}</td>
                            <td class="pe-4 text-end">
                                <span class="badge ${badgeClass} rounded-1 px-3 py-2">${wb.movementType}</span>
                            </td>
                        `;
                        tableBody.appendChild(tr);
                    });
                }
            } else {
                console.error('DEBUG: Table body #liveTrackerTable tbody not found');
            }
        }
    } catch (error) {
        console.error('DEBUG: Error updating dashboard:', error);
    }
}

// Ensure globally accessible
window.updateDashboard = updateDashboard;
