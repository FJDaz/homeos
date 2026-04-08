/**
 * TROUVER SON REPRÉSENTANT
 * Application citoyenne — Données ouvertes
 *
 * Sources :
 * - geo.api.gouv.fr (géocodage)
 * - data.assemblee-nationale.fr (députés)
 * - Fallbacks vers sites officiels
 */

// ============================================
// CONFIGURATION
// ============================================

const API = {
    GEO: 'https://api-adresse.data.gouv.fr',
    ASSEMBLEE: 'https://data.assemblee-nationale.fr',
};

// Mapping code région → site officiel
const REGION_SITES = {
    '01': { name: 'Guadeloupe', site: 'https://www.regionguadeloupe.fr' },
    '02': { name: 'Martinique', site: 'https://www.cr-martinique.fr' },
    '03': { name: 'Guyane', site: 'https://www.ctguyane.fr' },
    '04': { name: 'La Réunion', site: 'https://www.regionreunion.com' },
    '06': { name: 'Mayotte', site: 'https://www.departement976.fr' },
    '84': { name: 'Auvergne-Rhône-Alpes', site: 'https://www.auvergnerhonealpes.fr' },
    '27': { name: 'Bourgogne-Franche-Comté', site: 'https://www.bourgognefranchecomte.fr' },
    '53': { name: 'Bretagne', site: 'https://www.bretagne.bzh' },
    '24': { name: 'Centre-Val de Loire', site: 'https://www.centre-valdeloire.fr' },
    '94': { name: 'Corse', site: 'https://www.corsica.fr' },
    '44': { name: 'Grand Est', site: 'https://www.grandest.fr' },
    '32': { name: 'Hauts-de-France', site: 'https://www.hautsdefrance.fr' },
    '11': { name: 'Île-de-France', site: 'https://www.iledefrance.fr' },
    '28': { name: 'Normandie', site: 'https://www.normandie.fr' },
    '75': { name: 'Nouvelle-Aquitaine', site: 'https://www.nouvelle-aquitaine.fr' },
    '76': { name: 'Occitanie', site: 'https://www.laregionok.fr' },
    '52': { name: 'Pays de la Loire', site: 'https://www.paysdelaloire.fr' },
    '93': { name: "Provence-Alpes-Côte d'Azur", site: 'https://www.maregionsud.fr' },
};

// Mapping code département → site officiel
const DEPT_SITES = {
    // Métropole
    '01': 'https://www.ain.fr',
    '02': 'https://www.aisne.fr',
    '03': 'https://www.allier.fr',
    '04': 'https://www.alpesdehauteprovence.fr',
    '05': 'https://www.hautes-alpes.fr',
    '06': 'https://www.departement06.fr',
    '07': 'https://www.ardeche.fr',
    '08': 'https://www.ardeche.fr',
    '09': 'https://www.ariege.fr',
    '10': 'https://www.aube.fr',
    '11': 'https://www.aude.fr',
    '12': 'https://www.aveyron.fr',
    '13': 'https://www.departement13.fr',
    '14': 'https://www.calvados.fr',
    '15': 'https://www.cantal.fr',
    '16': 'https://www.charente.fr',
    '17': 'https://www.charente-maritime.fr',
    '18': 'https://www.cher.fr',
    '19': 'https://www.correze.fr',
    '2A': 'https://www.corse.fr',
    '2B': 'https://www.corse.fr',
    '21': 'https://www.cotedor.fr',
    '22': 'https://www.cotesdarmor.fr',
    '23': 'https://www.creuse.fr',
    '24': 'https://www.dordogne.fr',
    '25': 'https://www.doubs.fr',
    '26': 'https://www.ladrome.fr',
    '27': 'https://www.eure.fr',
    '28': 'https://www.eurelien.fr',
    '29': 'https://www.finistere.fr',
    '30': 'https://www.gard.fr',
    '31': 'https://www.haute-garonne.fr',
    '32': 'https://www.gers.fr',
    '33': 'https://www.gironde.fr',
    '34': 'https://www.herault.fr',
    '35': 'https://www.ille-et-vilaine.fr',
    '36': 'https://www.indre.fr',
    '37': 'https://www.touraine.fr',
    '38': 'https://www.isere.fr',
    '39': 'https://www.jura.fr',
    '40': 'https://www.landes.fr',
    '41': 'https://www.loir-et-cher.fr',
    '42': 'https://www.loire.fr',
    '43': 'https://www.hauteloire.fr',
    '44': 'https://www.loire-atlantique.fr',
    '45': 'https://www.loiret.fr',
    '46': 'https://www.lot.fr',
    '47': 'https://www.lotetgaronne.fr',
    '48': 'https://www.lozere.fr',
    '49': 'https://www.maine-et-loire.fr',
    '50': 'https://www.manche.fr',
    '51': 'https://www.marne.fr',
    '52': 'https://www.haute-marne.fr',
    '53': 'https://www.mayenne.fr',
    '54': 'https://www.meurthe-et-moselle.fr',
    '55': 'https://www.meuse.fr',
    '56': 'https://www.morbihan.fr',
    '57': 'https://www.moselle.fr',
    '58': 'https://www.nievre.fr',
    '59': 'https://www.lenord.fr',
    '60': 'https://www.oise.fr',
    '61': 'https://www.orne.fr',
    '62': 'https://www.pasdecalais.fr',
    '63': 'https://www.puy-de-dome.fr',
    '64': 'https://www.pyrenees-atlantiques.fr',
    '65': 'https://www.hautes-pyrenees.fr',
    '66': 'https://www.pyrenees-orientales.fr',
    '67': 'https://www.eurometropole.eu',
    '68': 'https://www.eurometropole.eu',
    '69': 'https://www.rhone.fr',
    '70': 'https://www.haute-saone.fr',
    '71': 'https://www.saone-et-loire.fr',
    '72': 'https://www.sarthe.fr',
    '73': 'https://www.savoie.fr',
    '74': 'https://www.haute-savoie.fr',
    '75': 'https://www.paris.fr',
    '76': 'https://www.seine-maritime.fr',
    '77': 'https://www.seine-et-marne.fr',
    '78': 'https://www.yvelines.fr',
    '79': 'https://www.deux-sevres.fr',
    '80': 'https://www.somme.fr',
    '81': 'https://www.tarn.fr',
    '82': 'https://www.tarn-et-garonne.fr',
    '83': 'https://www.var.fr',
    '84': 'https://www.vaucluse.fr',
    '85': 'https://www.vendee.fr',
    '86': 'https://www.vienne.fr',
    '87': 'https://www.haute-vienne.fr',
    '88': 'https://www.vosges.fr',
    '89': 'https://www.yonne.fr',
    '90': 'https://www.territoiredebelfort.fr',
    '91': 'https://www.essonne.fr',
    '92': 'https://www.hauts-de-seine.fr',
    '93': 'https://www.seine-saint-denis.fr',
    '94': 'https://www.valdemarne.fr',
    '95': 'https://www.valdoise.fr',
    // DOM
    '971': 'https://www.regionguadeloupe.fr',
    '972': 'https://www.cr-martinique.fr',
    '973': 'https://www.ctguyane.fr',
    '974': 'https://www.regionreunion.com',
    '976': 'https://www.departement976.fr',
};

// ============================================
// STATE
// ============================================

// (no global state needed — fully stateless)

// ============================================
// DOM HELPERS
// ============================================

const $ = (sel) => document.querySelector(sel);
const show = (el) => { if (el) el.hidden = false; };
const hide = (el) => { if (el) el.hidden = true; };
const setText = (sel, text) => { const el = $(sel); if (el) el.textContent = text; };

function showSection(id) {
    ['hero-section', 'loading-section', 'error-section', 'results-section'].forEach(s => {
        const el = $(`#${s}`);
        if (el) el.hidden = s !== id;
    });
}

function showError(title, message) {
    setText('#error-title', title);
    setText('#error-message', message);
    showSection('error-section');
}

// ============================================
// GEOCODING — geo.api.gouv.fr
// ============================================

async function geocodeAddress(query) {
    const url = `${API.GEO}/search/?q=${encodeURIComponent(query)}&limit=5`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Géocodage échoué (${res.status})`);
    const data = await res.json();
    if (!data.features || data.features.length === 0) {
        throw new Error('Aucune adresse trouvée');
    }
    return data.features;
}

function extractLocation(feature) {
    const props = feature.properties;

    console.log('Raw properties:', props);

    // Le champ "context" contient : "80, Somme, Hauts-de-France"
    // → [codeDept, nomDept, nomRegion]
    let departmentCode = '';
    let department = '';
    let region = '';
    let regionCode = '';

    if (props.context) {
        const parts = props.context.split(',').map(s => s.trim());
        departmentCode = parts[0] || '';
        department = parts[1] || '';
        region = parts[2] || '';

        // Mapping nom région → code
        regionCode = REGION_NAME_TO_CODE[region] || '';
    }

    // Fallback : extraire le code département du code postal
    if (!departmentCode && props.postcode) {
        departmentCode = props.postcode.substring(0, 2);
    }

    return {
        commune: props.city || '',
        communeCode: props.citycode || '',
        department: department,
        departmentCode: departmentCode,
        region: region,
        regionCode: regionCode,
        postcode: props.postcode || '',
        label: props.label || '',
        lat: feature.geometry.coordinates[1],
        lon: feature.geometry.coordinates[0],
    };
}

// Mapping nom de région → code région
const REGION_NAME_TO_CODE = {
    'Guadeloupe': '01',
    'Martinique': '02',
    'Guyane': '03',
    'La Réunion': '04',
    'Mayotte': '06',
    'Auvergne-Rhône-Alpes': '84',
    'Bourgogne-Franche-Comté': '27',
    'Bretagne': '53',
    'Centre-Val de Loire': '24',
    'Corse': '94',
    'Grand Est': '44',
    'Hauts-de-France': '32',
    'Île-de-France': '11',
    'Normandie': '28',
    'Nouvelle-Aquitaine': '75',
    'Occitanie': '76',
    'Pays de la Loire': '52',
    "Provence-Alpes-Côte d'Azur": '93',
};

// ============================================
// DÉPUTÉ — NosDéputés.fr (API open data fiable)
// ============================================

let _deputesCache = null;

async function loadDeputes() {
    if (_deputesCache) return _deputesCache;

    try {
        const url = 'https://www.nosdeputes.fr/deputes/json';
        const res = await fetch(url);
        if (!res.ok) throw new Error(`NosDéputés (${res.status})`);
        const data = await res.json();
        _deputesCache = data.deputes || [];
        return _deputesCache;
    } catch (e) {
        console.warn('loadDeputes error:', e);
        _deputesCache = [];
        return [];
    }
}

async function findDepute(departmentCode) {
    const deputes = await loadDeputes();
    if (!deputes.length) return null;

    // Filtrer par département (num_deptmt)
    const matches = deputes.filter(d => {
        const dp = d.depute.num_deptmt || '';
        return dp === departmentCode || dp.padStart(2, '0') === departmentCode;
    });

    if (!matches.length) return null;

    // Prendre le premier (idéalement on filtrerait par circonscription exacte)
    const d = matches[0].depute;
    const emails = d.emails || [];
    const sites = d.sites_web || [];

    return {
        nom: `${d.prenom || ''} ${d.nom_de_famille || ''}`.trim(),
        prenom: d.prenom || '',
        groupe: d.groupe_sigle || '',
        circonscription: d.nom_circo || '',
        email: emails.length > 0 ? emails[0].email || emails[0] : null,
        photo: null,
        ficheUrl: d.url_an || `https://www2.assemblee-nationale.fr/deputes/recherche-des-deputes`,
    };
}

// ============================================
// COMMUNE / MAIRIE
// ============================================

function getCommuneInfo(loc) {
    // Annuaire officiel du service public
    const communeSite = `https://www.google.com/search?q=mairie+${encodeURIComponent(loc.commune)}`;

    return {
        name: loc.commune ? `Mairie de ${loc.commune}` : 'Mairie',
        subtitle: loc.postcode ? `Code postal : ${loc.postcode}` : '',
        email: null,
        site: communeSite,
        siteText: 'Contacter la mairie',
    };
}

// ============================================
// RÉGION
// ============================================

function getRegionInfo(loc) {
    const code = loc.regionCode;
    const info = REGION_SITES[code] || null;

    return {
        name: info ? `Conseil régional ${info.name}` : (loc.region ? `Conseil régional ${loc.region}` : 'Conseil régional'),
        subtitle: loc.region ? `Code : ${code || '—'}` : '',
        email: null, // Pas d'email open data fiable
        site: info ? `${info.site}/contact` : `https://www.google.com/search?q=mairie+conseil+régional+${encodeURIComponent(loc.region)}`,
        siteText: 'Contacter le conseil régional',
    };
}

// ============================================
// DÉPARTEMENT
// ============================================

function getDepartementInfo(loc) {
    const code = loc.departmentCode;
    const site = DEPT_SITES[code] || null;
    const deptName = loc.department || (code ? `Département ${code}` : '');

    return {
        name: deptName ? `Conseil départemental ${deptName}` : 'Conseil départemental',
        subtitle: code ? `Code : ${code}` : '',
        email: null, // Pas d'email open data fiable
        site: site ? `${site}/contact` : `https://www.google.com/search?q=mairie+conseil+départemental+${encodeURIComponent(loc.department)}`,
        siteText: 'Contacter le conseil départemental',
    };
}

// ============================================
// RENDER
// ============================================

function renderResults(loc, depute, commune, region, dept) {
    // Location header
    const parts = [loc.commune, loc.department, loc.region].filter(Boolean);
    setText('#results-location', parts.join(', '));

    // --- DÉPUTÉ ---
    if (depute && depute.nom) {
        setText('#depute-name', depute.nom);
        setText('#depute-circo', depute.circonscription || '');
        setText('#depute-group', depute.groupe || '');

        const photoEl = $('#depute-photo');
        if (depute.photo) {
            photoEl.innerHTML = `<img src="${depute.photo}" alt="${depute.nom}" loading="lazy">`;
            show(photoEl);
        } else {
            hide(photoEl);
        }

        const emailEl = $('#depute-email');
        if (depute.email) {
            emailEl.href = `mailto:${depute.email}`;
            setText('#depute-email-text', depute.email);
            show(emailEl);
        } else {
            hide(emailEl);
        }

        const siteEl = $('#depute-site');
        siteEl.href = depute.ficheUrl;
    } else {
        setText('#depute-name', 'Député non trouvé');
        setText('#depute-circo', 'Les données de l\'Assemblée nationale ne sont pas disponibles en open data.');
        setText('#depute-group', '');
        hide($('#depute-photo'));
        hide($('#depute-email'));
        const siteEl = $('#depute-site');
        siteEl.href = `https://www2.assemblee-nationale.fr/deputes/recherche-des-deputes`;
        siteEl.querySelector('span').textContent = 'Trouver sur assemblee-nationale.fr';
    }

    // --- AUTRES REPRÉSENTANTS (liens) ---
    const mairieEl = $('#other-reps-mairie');
    mairieEl.href = commune.site;
    setText('#other-reps-mairie-desc', commune.siteText);

    const deptEl = $('#other-reps-dept');
    deptEl.href = dept.site;
    setText('#other-reps-dept-desc', dept.siteText);

    const regionEl = $('#other-reps-region');
    regionEl.href = region.site;
    setText('#other-reps-region-desc', region.siteText);

    showSection('results-section');
}

// ============================================
// MAIN FLOW
// ============================================

async function searchAddress(query) {
    showSection('loading-section');

    try {
        // 1. Géocodage
        const features = await geocodeAddress(query);
        const best = features[0];
        const loc = extractLocation(best);

        console.log('Location:', loc);

        // 2. Député
        const depute = await findDepute(loc.departmentCode);

        // 3. Commune, Région, Département
        const commune = getCommuneInfo(loc);
        const region = getRegionInfo(loc);
        const dept = getDepartementInfo(loc);

        // 4. Affichage
        renderResults(loc, depute, commune, region, dept);

    } catch (e) {
        console.error('Search error:', e);
        showError(
            'Adresse introuvable',
            e.message || 'Vérifiez votre saisie et réessayez.'
        );
    }
}

function resetSearch() {
    $('#street-input').value = '';
    $('#cp-input').value = '';
    showSection('hero-section');
    $('#street-input').focus();
}

// ============================================
// FORM SUBMIT
// ============================================

function setupForm() {
    const form = $('#search-form');
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const street = $('#street-input').value.trim();
        const cp = $('#cp-input').value.trim();

        if (!cp || cp.length !== 5 || !/^\d{5}$/.test(cp)) {
            showError('Code postal invalide', 'Le code postal doit contenir 5 chiffres.');
            return;
        }

        const query = street ? `${street}, ${cp}` : cp;
        searchAddress(query);
    });
}

// ============================================
// INIT
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    setupForm();
});
