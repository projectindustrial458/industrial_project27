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

        // Populate Platform Dropdown
        const sessionData = sessionStorage.getItem(AUTH_KEY);
        if (sessionData) {
            const data = JSON.parse(sessionData);
            const platformSelect = document.getElementById('platformNumber');
            if (platformSelect && data.platforms && data.platforms.length > 0) {
                // Keep the first default option
                platformSelect.innerHTML = '<option value="" disabled selected>PF</option>';
                data.platforms.forEach(pf => {
                    const option = document.createElement('option');
                    option.value = pf;
                    option.textContent = pf;
                    platformSelect.appendChild(option);
                });
            }
        }
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
    // Live Sequence Tracker Global Search
    const liveTrackerSearchInput = document.getElementById('liveTrackerSearchInput');
    let isGlobalSearchActive = false;

    if (liveTrackerSearchInput) {
        liveTrackerSearchInput.addEventListener('keypress', async function (e) {
            if (e.key === 'Enter') {
                const busNo = this.value.trim().toUpperCase();
                if (!busNo) {
                    isGlobalSearchActive = false;
                    updateDashboard();
                    return;
                }

                console.log(`DEBUG: Global search for bus: ${busNo}`);
                isGlobalSearchActive = true;

                try {
                    const response = await fetch(`/api/bus-history/${busNo}`);
                    const data = await response.json();

                    if (data.status === 'success') {
                        renderWaybillTable(data.waybills, true);
                    }
                } catch (error) {
                    console.error('DEBUG: Global search error:', error);
                }
            }
        });

        // Local filtering for quick interaction
        liveTrackerSearchInput.addEventListener('input', function () {
            if (isGlobalSearchActive) return; // Don't filter if we are in global mode

            const filter = this.value.toUpperCase();
            const table = document.getElementById('liveTrackerTable');
            const tr = table.getElementsByTagName('tr');

            for (let i = 1; i < tr.length; i++) {
                const txtBusNo = tr[i].getElementsByTagName('td')[0]?.textContent || "";
                tr[i].style.display = txtBusNo.toUpperCase().indexOf(filter) > -1 ? "" : "none";
            }
        });
    }

    // Initialize Dashboard Updates
    updateDashboard();
    updateMasterLog();

    // Auto-refresh logic
    setInterval(() => {
        if (!isGlobalSearchActive) {
            console.log('DEBUG: Auto-refreshing dashboard...');
            updateDashboard();
            updateMasterLog();
        }
    }, 10000);
});

async function updateMasterLog() {
    try {
        const response = await fetch('/api/master-log');
        const data = await response.json();

        if (data.status === 'success') {
            const dateEl = document.getElementById('masterLogDate');
            if (dateEl) dateEl.textContent = `Today, ${data.date}`;

            const tableBody = document.getElementById('dailyLogTableBody');
            if (!tableBody) return;

            tableBody.innerHTML = '';

            if (data.waybills.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="10" class="text-center py-4 text-muted">No movements recorded for today yet.</td></tr>';
                return;
            }

            data.waybills.forEach(wb => {
                const tr = document.createElement('tr');

                // Movement Check
                let schArr = '-', actArr = '-', schDep = '-', actDep = '-';
                if (wb.movementType === 'Arrival') {
                    schArr = wb.scheduledTime;
                    actArr = wb.actualTime;
                } else {
                    schDep = wb.scheduledTime;
                    actDep = wb.actualTime;
                }

                tr.innerHTML = `
                    <td class="ps-4 fw-bold">${wb.busRegNo}</td>
                    <td>${wb.serviceCategory}</td>
                    <td>${wb.route}</td>
                    <td>${schArr}</td>
                    <td class="${actArr > schArr ? 'text-danger' : 'text-success'}">${actArr}</td>
                    <td>${schDep}</td>
                    <td class="${actDep > schDep ? 'text-danger' : 'text-success'}">${actDep}</td>
                    <td><span class="badge border bg-light text-dark">${wb.alerts}</span></td>
                    <td class="pe-4 text-end">
                        <span class="badge ${wb.statusClass} rounded-pill px-3">${wb.status}</span>
                    </td>
                `;
                tableBody.appendChild(tr);
            });
        }
    } catch (error) {
        console.error('DEBUG: Error updating Master Log:', error);
    }
}

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
                        depotName: data.depot_name || "",
                        platforms: data.platforms || [],
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

            // Update Platforms
            updatePlatforms(data.waybills);

            // Update Table
            renderWaybillTable(data.waybills);
        }
    } catch (error) {
        console.error('DEBUG: Error updating dashboard:', error);
    }
}

function renderWaybillTable(waybills, isGlobal = false) {
    const tableBody = document.querySelector('#liveTrackerTable tbody');
    const sessionData = sessionStorage.getItem('ksrtc_sm_session');
    if (!tableBody || !sessionData) return;

    const session = JSON.parse(sessionData);
    tableBody.innerHTML = '';

    if (waybills.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="10" class="text-center py-4 text-muted">${isGlobal ? 'No history found for this bus.' : 'No live data available for this depot yet.'}</td></tr>`;
        return;
    }

    waybills.forEach(wb => {
        const tr = document.createElement('tr');

        let schArr = '-', actArr = '-', schDep = '-', actDep = '-';
        let badgeClass = '';

        if (wb.movementType === 'Arrival') {
            schArr = wb.scheduledTime;
            actArr = wb.actualTime;
            badgeClass = 'bg-success-subtle text-success';
        } else {
            schDep = wb.scheduledTime;
            actDep = wb.actualTime;
            badgeClass = 'bg-warning-subtle text-warning';
        }

        let isDelayed = wb.actualTime > wb.scheduledTime;
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
            <td><span class="badge ${wb.depot_id === session.depotId ? 'bg-light text-dark' : 'bg-info-subtle text-info'}">${wb.depot_id}</span></td>
            <td class="pe-4 text-end">
                <span class="badge ${badgeClass} rounded-1 px-3 py-2">${wb.movementType}</span>
            </td>
        `;
        tableBody.appendChild(tr);
    });
}

// Update dynamic platform bays
function updatePlatforms(waybills) {
    const container = document.getElementById('platformsContainer');
    const template = document.getElementById('platformCardTemplate');
    const sessionData = sessionStorage.getItem('ksrtc_sm_session');

    if (!container || !template || !sessionData) return;

    const session = JSON.parse(sessionData);
    const platforms = session.platforms || [];

    if (platforms.length === 0) {
        container.innerHTML = '<div class="col-12 text-center py-4 text-muted">No platforms configured for this depot.</div>';
        return;
    }

    container.innerHTML = ''; // Clear current

    // Logic to find current bus at each platform
    // Sort waybills by timestamp (most recent first) - usually already sorted from API

    platforms.forEach(pf => {
        // Find most recent waybill for this platform
        const latestWaybill = waybills.find(wb => wb.platformNumber === pf);

        const clone = template.content.cloneNode(true);
        const card = clone.querySelector('.card');
        const pfName = clone.querySelector('.pf-name');
        const pfStatus = clone.querySelector('.pf-status');
        const pfBusGraphic = clone.querySelector('.pf-bus-graphic');
        const pfRoute = clone.querySelector('.pf-route');
        const pfTime = clone.querySelector('.pf-time');

        pfName.textContent = `P-${pf}`;

        if (latestWaybill && latestWaybill.movementType === 'Arrival') {
            // OCCUPIED
            card.classList.add('pf-occupied');
            pfStatus.textContent = 'OCCUPIED';
            pfStatus.classList.add('pf-status-occupied');

            pfBusGraphic.innerHTML = `
                <div class="bg-light rounded p-3 d-inline-block position-relative bus-active">
                    <i class="bi bi-bus-front-fill fs-1 text-danger"></i>
                    <div class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-dark">
                        ${latestWaybill.busRegNo.split('-').slice(0, 2).join('-')}
                    </div>
                </div>
            `;
            pfRoute.textContent = `${latestWaybill.origin} - ${latestWaybill.destination}`;
            pfTime.textContent = `Arr: ${latestWaybill.actualTime}`;
        } else {
            // EMPTY
            card.classList.add('pf-empty');
            pfStatus.textContent = 'EMPTY';
            pfStatus.classList.add('pf-status-empty');

            pfBusGraphic.innerHTML = `
                <div class="bg-light rounded p-3 d-inline-block position-relative opacity-25">
                    <i class="bi bi-slash-circle fs-1 text-secondary"></i>
                </div>
            `;
            pfRoute.textContent = 'Available';
            pfTime.textContent = '--:--';
        }

        container.appendChild(clone);
    });
}

// Bus Search Records Handler
const busSearchForm = document.getElementById('busSearchForm');
if (busSearchForm) {
    busSearchForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const date = document.getElementById('historySearchDate').value;
        const busNo = document.getElementById('historySearchBusNo').value;
        const depotId = document.getElementById('historySearchDepot').value;
        const movementType = document.getElementById('historySearchType').value;

        const btn = busSearchForm.querySelector('button[type="submit"]');
        const originalBtnContent = btn.innerHTML;
        const resultsDiv = document.getElementById('searchResults');
        const resultsTableBody = document.querySelector('#historyResultsTable tbody');
        const resultCountBadge = document.getElementById('searchResultCount');

        try {
            btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
            btn.disabled = true;

            const queryParams = new URLSearchParams({
                date,
                busNo,
                depotId,
                movementType
            });

            const response = await fetch(`/api/search?${queryParams.toString()}`);
            const data = await response.json();

            if (data.status === 'success') {
                resultsDiv.classList.remove('d-none');
                resultCountBadge.textContent = `${data.count} Records Found`;
                resultsTableBody.innerHTML = '';

                if (data.waybills.length === 0) {
                    resultsTableBody.innerHTML = '<tr><td colspan="8" class="text-center py-4 text-muted">No records matching your search.</td></tr>';
                } else {
                    data.waybills.forEach(wb => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td class="ps-4 fw-medium">${wb.timestamp}</td>
                            <td class="fw-bold">${wb.busRegNo}</td>
                            <td><span class="badge border text-dark rounded-pill fw-normal px-2">${wb.serviceCategory}</span></td>
                            <td>${wb.origin} - ${wb.destination}</td>
                            <td><span class="badge ${wb.movementType === 'Arrival' ? 'bg-success-subtle text-success' : 'bg-warning-subtle text-warning'} rounded-1 px-2 py-1">${wb.movementType}</span></td>
                            <td>${wb.origin}</td>
                            <td>${wb.destination}</td>
                            <td class="pe-4 text-end"><span class="badge bg-light text-dark">${wb.depot_id}</span></td>
                        `;
                        resultsTableBody.appendChild(tr);
                    });
                }

                // Scroll to results
                resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

            } else {
                alert('Search failed: ' + data.message);
            }
        } catch (error) {
            console.error('Error searching records:', error);
            alert('An error occurred during search.');
        } finally {
            btn.innerHTML = originalBtnContent;
            btn.disabled = false;
        }
    });
}
