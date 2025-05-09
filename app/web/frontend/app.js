let currentPage = 1;
const perPage = 50;

document.addEventListener('DOMContentLoaded', async () => {
	try {
		await loadReports();
		await loadEmailStats();
		setupFilters();
		// load by default all filters
		loadEmailsByFilters();
	} catch (error) {
		console.error('Error while loading app :', error);
	}
});

async function loadReports() {
	const response = await fetch('/reports');
	const reports = await response.json();

	const tableBody = document.getElementById('reportTableBody');
	tableBody.innerHTML = '';

	reports.forEach(report => {
		const row = document.createElement('tr');
		row.innerHTML = `
            <td class="border px-4 py-2">${report.id}</td>
            <td class="border px-4 py-2">${report.org_name}</td>
            <td class="border px-4 py-2">${report.domain}</td>
            <td class="border px-4 py-2">${new Date(report.date_begin).toLocaleDateString()}</td>
            <td class="border px-4 py-2">${new Date(report.date_end).toLocaleDateString()}</td>
            <td class="border px-4 py-2">${report.policy}</td>
            <td class="border px-4 py-2">${report.email_count}</td>
        `;
		tableBody.appendChild(row);
	});
}

async function loadEmailStats() {
	const queries = [
		fetch('/emails?disposition=none&spf=pass&dkim=pass&page=1&per_page=1'),
		fetch('/emails?disposition=none&spf=fail&dkim=fail&page=1&per_page=1'),
		fetch('/emails?disposition=quarantine&page=1&per_page=1'),
		fetch('/emails?disposition=reject&page=1&per_page=1')
	];

	const [passResp, passSPFDKIMErrorResp, quarantineResp, rejectResp] = await Promise.all(queries);
	const passData = await passResp.json();
	const passSPFDKIMErrorCount = await passSPFDKIMErrorResp.json();
	const quarantineData = await quarantineResp.json();
	const rejectData = await rejectResp.json();

	document.getElementById('passCount').textContent = passData.meta.total;
	document.getElementById('passSPFDKIMErrorCount').textContent = passSPFDKIMErrorCount.meta.total;
	document.getElementById('quarantineCount').textContent = quarantineData.meta.total;
	document.getElementById('rejectCount').textContent = rejectData.meta.total;

	const ctx = document.getElementById('statusChart').getContext('2d');
	new Chart(ctx, {
		type: 'doughnut',
		data: {
			labels: ['Pass', 'Pass (SPF or DKIM fail)', 'Quarantine', 'Reject'],
			datasets: [{
				data: [
					passData.meta.total,
					passSPFDKIMErrorCount.meta.total,
					quarantineData.meta.total,
					rejectData.meta.total
				],
				backgroundColor: ['#228b22', '#38bdf8', '#facc15', '#f87171'],
			}]
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
		}
	});
}

function buildFilterQuery() {
	const params = new URLSearchParams();
	document.querySelectorAll('input[type="checkbox"][data-filter]').forEach(cb => {
		if (cb.checked) {
			params.append(cb.getAttribute('data-filter'), cb.value);
		}
	});
	return params.toString();
}

async function loadEmailsByFilters() {
	const params = new URLSearchParams(buildFilterQuery());
	params.set("page", currentPage);
	params.set("per_page", perPage);

	const resp = await fetch(`/emails?${params.toString()}`);
	const json = await resp.json();

	renderEmailTable(json.data);
	renderPaginationControls(json.meta);
}


// Remplit le tableau d'emails
function renderEmailTable(emails) {
	const tbody = document.getElementById('emailTableBody');
	tbody.innerHTML = '';
	emails.forEach(e => {
		const tr = document.createElement('tr');
		tr.innerHTML = `
        <td class="border px-4 py-2"><a target="_blank" rel="noopener noreferrer" href="report/${e.report_id}/xml">View XML report</a></td>
        <td class="border px-4 py-2">${e.source_ip}</td>
        <td class="border px-4 py-2">${e.header_from}</td>
        <td class="border px-4 py-2">${e.disposition}</td>
        <td class="border px-4 py-2">${e.spf_result}</td>
        <td class="border px-4 py-2">${e.dkim_result}</td>
      `;
		tbody.appendChild(tr);
	});
}

// Aply presets
function applyPreset(preset) {
	// Uncheck all checkboxes
	document.querySelectorAll('input[type="checkbox"][data-filter]').forEach(cb => cb.checked = false);
	currentPage = 1;

	switch (preset) {
		case 'all':
			document.querySelectorAll('input[type="checkbox"][data-filter]').forEach(cb => cb.checked = false);
			break;
		case 'reject':
			document.querySelector('input[data-filter="disposition"][value="reject"]').checked = true;
			break;
		case 'quarantine':
			document.querySelector('input[data-filter="disposition"][value="quarantine"]').checked = true;
			break;
		case 'pass':
			['none', 'pass', 'pass'].forEach((val, i) => {
				const type = ['disposition', 'spf', 'dkim'][i];
				document.querySelector(`input[data-filter="${type}"][value="${val}"]`).checked = true;
			});
			break;
		case 'pass-partial':
			document.querySelector('input[data-filter="disposition"][value="none"]').checked = true;
			document.querySelector('input[data-filter="spf"][value="fail"]').checked = true;
			document.querySelector('input[data-filter="dkim"][value="fail"]').checked = true;
			break;
	}
	loadEmailsByFilters();
}

function setupFilters() {
	document.querySelectorAll('input[type="checkbox"][data-filter]')
		.forEach(cb => cb.addEventListener('change', loadEmailsByFilters));

	// presets
	document.getElementById('preset-all')
		.addEventListener('click', () => applyPreset('all'));
	document.getElementById('preset-reject')
		.addEventListener('click', () => applyPreset('reject'));
	document.getElementById('preset-quarantine')
		.addEventListener('click', () => applyPreset('quarantine'));
	document.getElementById('preset-pass')
		.addEventListener('click', () => applyPreset('pass'));
	document.getElementById('preset-pass-partial')
		.addEventListener('click', () => applyPreset('pass-partial'));
}

function renderPaginationControls(meta) {
	const container = document.getElementById("pagination");
	container.innerHTML = "";

	// Button « Previous »
	const prev = document.createElement("button");
	prev.textContent = "« Prev";
	prev.disabled = !meta.prev;
	prev.className = prev.disabled ? "opacity-50 px-3 py-1" : "px-3 py-1 bg-gray-200";
	prev.onclick = () => {
		currentPage--;
		loadEmailsByFilters();
	};
	container.appendChild(prev);

	// Info actual page
	const info = document.createElement("span");
	info.textContent = `Page ${meta.page} / ${meta.total_pages}`;
	info.className = "px-3 py-1";
	container.appendChild(info);

	// Button « Next »
	const next = document.createElement("button");
	next.textContent = "Next »";
	next.disabled = !meta.next;
	next.className = next.disabled ? "opacity-50 px-3 py-1" : "px-3 py-1 bg-gray-200";
	next.onclick = () => {
		currentPage++;
		loadEmailsByFilters();
	};
	container.appendChild(next);
}