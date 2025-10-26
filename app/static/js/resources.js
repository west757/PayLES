
// --- Resource Metadata ---
const RESOURCE_CATEGORIES = [
	{ key: 'General', label: 'General' },
	{ key: 'Financial', label: 'Financial' },
	{ key: 'PCS/Moving', label: 'PCS/Moving' },
	{ key: 'Travel', label: 'Travel' },
	{ key: 'Education', label: 'Education' },
	{ key: 'Health', label: 'Health' },
    { key: 'Legal', label: 'Legal' },
	{ key: 'Resource List', label: 'Resource List' },
	{ key: 'Calculator', label: 'Calculator' },
];
const RESOURCE_BRANCHES = [
	{ key: 'DoD', label: 'DoD' },
    { key: 'U.S. Army', label: 'U.S. Army' },
	{ key: 'U.S. Air Force', label: 'U.S. Air Force' },
	{ key: 'U.S. Space Force', label: 'U.S. Space Force' },
	{ key: 'U.S. Navy', label: 'U.S. Navy' },
	{ key: 'U.S. Marine Corps', label: 'U.S. Marine Corps' },
    { key: 'Non-DoD', label: 'Non-DoD' },
];

// --- Utility: Star Icon SVG ---
function getStarIcon() {
	return `<span class="resource-featured-star" title="Featured Resource">★</span>`;
}

async function fetchAndFlattenResources() {
    // Fetch the JSON file
    const resp = await fetch('/static/json/resources.json');
    const data = await resp.json();
    // data is already a flat array of resources
    // Ensure category and branch are arrays, and featured is boolean
    let flat = data.map(item => ({
        ...item,
        category: Array.isArray(item.category) ? item.category : [],
        branch: Array.isArray(item.branch) ? item.branch : [],
        featured: !!item.featured,
    }));
    // Sort alphabetically by name
    flat.sort((a, b) => a.name.localeCompare(b.name));
    return flat;
}

// --- Render Category and Branch Filters ---
function renderCategoryFilters(selected) {
	const container = document.getElementById('resources-category-filters');
	container.innerHTML = '';
	RESOURCE_CATEGORIES.forEach(cat => {
		const id = `cat-filter-${cat.key}`;
		const checked = selected.includes(cat.key) ? 'checked' : '';
		container.innerHTML += `
			<label class="resources-filter-label" for="${id}">
				<input type="checkbox" class="resources-filter-checkbox" id="${id}" value="${cat.key}" ${checked} />
				${cat.label}
			</label>
		`;
	});
}

function renderBranchFilters(selected) {
	const container = document.getElementById('resources-branch-filters');
	container.innerHTML = '';
	RESOURCE_BRANCHES.forEach(branch => {
		const id = `branch-filter-${branch.key.replace(/\s/g, '-')}`;
		const checked = selected.includes(branch.key) ? 'checked' : '';
		container.innerHTML += `
			<label class="resources-filter-label" for="${id}">
				<input type="checkbox" class="resources-filter-checkbox" id="${id}" value="${branch.key}" ${checked} />
				${branch.label}
			</label>
		`;
	});
}

// --- Render Resource List ---
function renderResourceList(resources) {
	const container = document.getElementById('resources-container');
	if (!resources.length) {
		container.innerHTML = '<div style="margin:2em 0;color:#888;">No resources found.</div>';
		return;
	}
	container.innerHTML = `<div class="resources-list">${resources.map(resource => {
		const star = resource.featured ? getStarIcon() : '';
		const cats = (resource.category || []).map(cat => `<span class="resource-category-badge">${cat}</span>`).join('');
		const branches = (resource.branch || []).map(br => `<span class="resource-branch-badge">${br}</span>`).join('');
		return `
			<div class="resource-rect" tabindex="0" onclick="window.open('${resource.url}','_blank')" title="${resource.name}">
				${star}
				<div class="resource-main">
					<div class="resource-name">${resource.name}</div>
					<div class="resource-desc">${resource.desc || ''}</div>
					<div class="resource-meta">${cats}${branches}</div>
				</div>
			</div>
		`;
	}).join('')}</div>`;
}

window.initResourcesPage = async function initResourcesPage() {
    let allResources = await fetchAndFlattenResources();
    let searchValue = '';
    let selectedCategories = [];
    let selectedBranches = [];

    // Render filters
    renderCategoryFilters(selectedCategories);
    renderBranchFilters(selectedBranches);

    // --- Filtering Logic ---
    function filterResources() {
        let filtered = allResources;
        // Search by name
        if (searchValue) {
            const sv = searchValue.toLowerCase();
            filtered = filtered.filter(r => r.name.toLowerCase().includes(sv));
        }
        // Filter by categories (if any selected)
        if (selectedCategories.length) {
            filtered = filtered.filter(r =>
                (r.category || []).some(cat => selectedCategories.includes(cat))
            );
        }
        // Filter by branches (if any selected)
        if (selectedBranches.length) {
            filtered = filtered.filter(r =>
                (r.branch || []).some(br => selectedBranches.includes(br))
            );
        }
        renderResourceList(filtered);
    }

    // --- Event Listeners ---
    // Search bar
    const searchBar = document.getElementById('resources-search-bar');
    searchBar.addEventListener('input', e => {
        searchValue = e.target.value.slice(0, 40);
        filterResources();
    });

    // Category checkboxes
    document.getElementById('resources-category-filters').addEventListener('change', e => {
        if (e.target.classList.contains('resources-filter-checkbox')) {
            const val = e.target.value;
            if (e.target.checked) {
                if (!selectedCategories.includes(val)) selectedCategories.push(val);
            } else {
                selectedCategories = selectedCategories.filter(c => c !== val);
            }
            filterResources();
        }
    });

    // Branch checkboxes
    document.getElementById('resources-branch-filters').addEventListener('change', e => {
        if (e.target.classList.contains('resources-filter-checkbox')) {
            const val = e.target.value;
            if (e.target.checked) {
                if (!selectedBranches.includes(val)) selectedBranches.push(val);
            } else {
                selectedBranches = selectedBranches.filter(b => b !== val);
            }
            filterResources();
        }
    });

    // Initial render
    filterResources();
};