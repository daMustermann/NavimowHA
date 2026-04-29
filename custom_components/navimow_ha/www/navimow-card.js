/**
 * navimow-card.js — Navimow Live Map & Control Card for Home Assistant
 *
 * Automatically registered when the Navimow HA integration is loaded.
 * No manual installation needed — just add the card via the UI card picker.
 *
 * Card type:   custom:navimow-card
 * Minimal config:
 *   type: custom:navimow-card
 *   entity_prefix: navimow_m550   ← prefix of your device entities
 *
 * The entity_prefix is the part before the first underscore-delimited suffix
 * in your sensor entity IDs, e.g. from sensor.navimow_m550_battery → navimow_m550.
 *
 * Full config options:
 *   entity_prefix:   string   (required) e.g. "navimow_m550"
 *   range:           number   Map radius in meters (default: 12)
 *   show_map:        boolean  Show live SVG map    (default: true)
 *   show_controls:   boolean  Show control buttons (default: true)
 *   show_stats:      boolean  Show stats row       (default: true)
 *   show_settings:   boolean  Show settings panel  (default: false)
 */

const NAVIMOW_CARD_VERSION = '1.0.0';

// ── Defaults ────────────────────────────────────────────────────────────────
const DEFAULTS = { range: 12, show_map: true, show_controls: true, show_stats: true, show_settings: false };

const STATUS_COLOR = { mowing: '#4CAF50', charging: '#FFC107', docked: '#2196F3', paused: '#FF9800', error: '#f44336' };
const STATUS_LABEL = { mowing: 'MÄHT', charging: 'LÄDT', docked: 'GEPARKT', paused: 'PAUSE', error: 'FEHLER' };

// ── Editor schema for ha-form ────────────────────────────────────────────────
const EDITOR_SCHEMA = [
  {
    name: 'entity_prefix',
    required: true,
    label: 'Entitätspräfix',
    description: 'z.B. navimow_m550 (aus sensor.navimow_m550_battery)',
    selector: { text: {} },
  },
  {
    name: 'range',
    label: 'Kartenradius (Meter)',
    description: 'Radius des dargestellten Mähbereichs',
    selector: { number: { min: 2, max: 60, step: 1, mode: 'slider' } },
  },
  { name: 'show_map',      label: 'Live-Karte anzeigen',      selector: { boolean: {} } },
  { name: 'show_controls', label: 'Steuerung anzeigen',        selector: { boolean: {} } },
  { name: 'show_stats',    label: 'Statistiken anzeigen',      selector: { boolean: {} } },
  { name: 'show_settings', label: 'Einstellungen anzeigen',    selector: { boolean: {} } },
];

// ── Styles ───────────────────────────────────────────────────────────────────
const STYLES = `
  :host { display: block; }
  ha-card { overflow: hidden; background: var(--card-background-color); border-radius: var(--ha-card-border-radius, 12px); }

  /* Map */
  .map-wrap { background: linear-gradient(155deg,#091509 0%,#162e16 60%,#0c1f0c 100%); line-height: 0; }
  .map-wrap svg { display: block; width: 100%; height: auto; }
  .map-offline { display: flex; flex-direction: column; align-items: center; justify-content: center;
    padding: 32px; gap: 8px; color: rgba(255,255,255,0.35); font-size: 13px; font-family: sans-serif;
    background: linear-gradient(155deg,#091509,#162e16,#0c1f0c); min-height: 120px; }
  .map-offline ha-icon { --mdc-icon-size: 40px; color: rgba(255,255,255,0.15); }

  /* Header */
  .header { display: flex; align-items: center; justify-content: space-between; padding: 14px 16px 6px; }
  .title { font-size: 15px; font-weight: 700; color: var(--primary-text-color); display: flex; align-items: center; gap: 8px; }
  .title ha-icon { --mdc-icon-size: 20px; color: #4CAF50; }
  .badge { font-size: 10px; font-weight: 800; padding: 3px 10px; border-radius: 12px;
    letter-spacing: 0.8px; color: white; text-transform: uppercase; }

  /* Controls */
  .controls { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; padding: 10px 14px; }
  .btn { display: flex; flex-direction: column; align-items: center; gap: 5px; padding: 12px 4px;
    border: none; border-radius: 12px; cursor: pointer; font-size: 11px; font-weight: 700;
    font-family: inherit; color: var(--primary-text-color); background: var(--secondary-background-color);
    transition: all 0.2s ease; -webkit-tap-highlight-color: transparent; }
  .btn:active { transform: scale(0.93); }
  .btn:hover  { filter: brightness(1.12); }
  .btn ha-icon { --mdc-icon-size: 26px; }
  .btn.act-start { background: linear-gradient(145deg,#1b5e20,#2e7d32); color:#fff; box-shadow:0 4px 14px rgba(76,175,80,.35); }
  .btn.act-pause { background: linear-gradient(145deg,#bf360c,#e64a19); color:#fff; box-shadow:0 4px 14px rgba(255,87,34,.35); }
  .btn.act-dock  { background: linear-gradient(145deg,#0d47a1,#1565c0); color:#fff; box-shadow:0 4px 14px rgba(33,150,243,.35); }
  .btn ha-icon[slot] { color: inherit; }

  /* Stats */
  .stats { display: grid; grid-template-columns: repeat(3,1fr); padding: 2px 14px 12px; }
  .stat { display: flex; flex-direction: column; align-items: center; padding: 8px 4px; gap: 2px; }
  .stat-val { font-size: 17px; font-weight: 700; color: var(--primary-text-color); line-height:1.1; }
  .stat-lbl { font-size: 9px; color: var(--secondary-text-color); text-transform: uppercase; letter-spacing:.5px; text-align:center; }
  .stat-ico { --mdc-icon-size:16px; color: var(--secondary-text-color); margin-bottom:2px; }
  .divider { height: 1px; background: var(--divider-color); margin: 0 14px; }

  /* Settings */
  .settings { padding: 10px 14px; display: flex; flex-direction: column; gap: 6px; }
  .setting-row { display: flex; align-items: center; justify-content: space-between;
    font-size: 13px; color: var(--primary-text-color); min-height: 40px; }
  .setting-lbl { display: flex; align-items: center; gap: 10px; flex: 1; }
  .setting-lbl ha-icon { --mdc-icon-size: 18px; color: var(--secondary-text-color); }
  .height-ctrl { display: flex; align-items: center; gap: 6px; }
  .height-val { font-size: 14px; font-weight: 700; min-width: 44px; text-align: center;
    color: var(--primary-text-color); }
  .height-btn { width: 28px; height: 28px; border: 1px solid var(--divider-color); border-radius: 50%;
    background: var(--secondary-background-color); cursor: pointer; font-size: 16px;
    display: flex; align-items: center; justify-content: center; color: var(--primary-text-color);
    transition: all 0.15s; padding: 0; }
  .height-btn:hover { background: var(--primary-color); color: white; border-color: transparent; }
  .height-btn:active { transform: scale(0.9); }

  /* Toggle settings row */
  .sect-label { font-size: 10px; font-weight: 600; text-transform: uppercase;
    letter-spacing: .8px; color: var(--secondary-text-color); padding: 10px 14px 2px; }

  /* Error */
  .error-bar { display: flex; align-items: center; gap: 10px; background: rgba(244,67,54,0.1);
    border-left: 3px solid #f44336; margin: 6px 14px; padding: 10px 12px;
    border-radius: 0 8px 8px 0; font-size: 12px; color: #ef5350; }
  .error-bar ha-icon { --mdc-icon-size: 18px; flex-shrink: 0; }

  /* Unconfigured */
  .unconfigured { display: flex; flex-direction: column; align-items: center; gap: 12px;
    padding: 28px 20px; text-align: center; }
  .unconfigured ha-icon { --mdc-icon-size: 48px; color: var(--secondary-text-color); }
  .unconfigured .unc-title { font-size: 14px; font-weight: 600; color: var(--primary-text-color); }
  .unconfigured .unc-hint { font-size: 12px; color: var(--secondary-text-color); }
`;

// ── SVG map builder ───────────────────────────────────────────────────────────
function buildMapSVG(states, cfg) {
  const W = 320, H = 280, M = 28;
  const R = cfg.range || 12;
  const x  = parseFloat(states.x)     || 0;
  const y  = parseFloat(states.y)     || 0;
  const th = parseFloat(states.theta) || 0;
  const st = states.status || 'unknown';
  const bat = Math.max(0, Math.min(100, parseInt(states.battery) || 0));

  const isMowing   = st === 'mowing';
  const mc = STATUS_COLOR[st] || '#78909C';
  const ml = STATUS_LABEL[st] || st.toUpperCase();

  const mapW = W - 2*M, mapH = H - 2*M;
  const mX = M + mapW/2 + (x/R)*(mapW/2);
  const mY = M + mapH/2 - (y/R)*(mapH/2);
  const aDeg = (th * 180/Math.PI) - 90;

  // Unique ID suffix to avoid filter/gradient clashes if multiple cards
  const uid = (cfg.entity_prefix || 'nav').replace(/[^a-z0-9]/gi,'');

  // Grid
  let grid = '';
  for (let i=0; i<=4; i++) {
    const gx=(M+(i/4)*mapW).toFixed(1), gy=(M+(i/4)*mapH).toFixed(1);
    const a = i===2?'0.22':'0.07';
    grid += `<line x1="${gx}" y1="${M}" x2="${gx}" y2="${H-M}" stroke="rgba(144,210,144,${a})" stroke-width="1"/>`;
    grid += `<line x1="${M}" y1="${gy}" x2="${W-M}" y2="${gy}" stroke="rgba(144,210,144,${a})" stroke-width="1"/>`;
  }

  const batW = 68;
  const batColor = bat>50?'#4CAF50':bat>20?'#FFC107':'#f44336';
  const dist = Math.sqrt(x*x+y*y).toFixed(1);

  const pulse = isMowing ? `
    <circle r="12" fill="${mc}" opacity="0">
      <animate attributeName="r" values="12;26;12" dur="2.2s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.5;0;0.5" dur="2.2s" repeatCount="indefinite"/>
    </circle>` : '';

  const blade = isMowing
    ? `<g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="0.9s" repeatCount="indefinite"/>
         <line x1="-6" y1="0" x2="6" y2="0" stroke="rgba(255,255,255,.8)" stroke-width="2.5" stroke-linecap="round"/>
         <line x1="0" y1="-6" x2="0" y2="6" stroke="rgba(255,255,255,.8)" stroke-width="2.5" stroke-linecap="round"/>
       </g>`
    : `<line x1="-5" y1="0" x2="5" y2="0" stroke="rgba(255,255,255,.4)" stroke-width="2" stroke-linecap="round"/>
       <line x1="0" y1="-5" x2="0" y2="5" stroke="rgba(255,255,255,.4)" stroke-width="2" stroke-linecap="round"/>`;

  return `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="ng-${uid}" cx="50%" cy="50%" r="55%">
      <stop offset="0%" stop-color="#2d6a2d" stop-opacity="0.45"/>
      <stop offset="100%" stop-color="#1a3d1a" stop-opacity="0"/>
    </radialGradient>
    <filter id="gl-${uid}"><feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <filter id="sg-${uid}"><feGaussianBlur stdDeviation="2" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <rect width="${W}" height="${H}" fill="url(#ng-${uid})"/>
  <rect x="${M}" y="${M}" width="${mapW}" height="${mapH}" fill="rgba(0,60,0,.18)"
        stroke="rgba(144,210,144,.18)" stroke-width="1" rx="6"/>
  ${grid}
  <!-- Scale bar -->
  <line x1="${M+4}" y1="${H-M+7}" x2="${M+4+mapW/4}" y2="${H-M+7}" stroke="#4CAF50" stroke-width="1.5" stroke-linecap="round"/>
  <line x1="${M+4}"         y1="${H-M+4}" x2="${M+4}"         y2="${H-M+10}" stroke="#4CAF50" stroke-width="1.5"/>
  <line x1="${M+4+mapW/4}"  y1="${H-M+4}" x2="${M+4+mapW/4}"  y2="${H-M+10}" stroke="#4CAF50" stroke-width="1.5"/>
  <text x="${(M+4+mapW/8+8).toFixed(0)}" y="${H-M+18}" text-anchor="middle" font-size="8"
        fill="#4CAF50" opacity=".7" font-family="monospace">${(R/2).toFixed(0)}m</text>
  <!-- Charging station -->
  <g transform="translate(${M+mapW/2},${M+mapH/2})" filter="url(#gl-${uid})">
    <circle r="11" fill="#FFC107" opacity=".9"/>
    <text text-anchor="middle" dominant-baseline="middle" font-size="11">⚡</text>
  </g>
  <!-- Mower shadow -->
  <ellipse cx="${(mX+2).toFixed(1)}" cy="${(mY+3).toFixed(1)}" rx="13" ry="7" fill="rgba(0,0,0,.35)"/>
  <!-- Mower -->
  <g transform="translate(${mX.toFixed(1)},${mY.toFixed(1)})" filter="url(#sg-${uid})">
    ${pulse}
    <circle r="12" fill="${mc}" opacity=".92"/>
    <g transform="rotate(${aDeg.toFixed(1)})">
      <polygon points="0,-17 -5,-8 5,-8" fill="white" opacity=".85"/>
    </g>
    ${blade}
    <circle r="2.5" fill="white" opacity=".9"/>
  </g>
  <!-- Coord box -->
  <rect x="4" y="4" width="102" height="46" rx="7" fill="rgba(0,0,0,.62)"/>
  <text x="10" y="18" font-size="9" fill="rgba(255,255,255,.75)" font-family="monospace">X ${x>=0?'+':''}${x.toFixed(2)} m</text>
  <text x="10" y="30" font-size="9" fill="rgba(255,255,255,.75)" font-family="monospace">Y ${y>=0?'+':''}${y.toFixed(2)} m</text>
  <text x="10" y="42" font-size="8"  fill="rgba(255,255,255,.4)"  font-family="monospace">∅${dist}m · θ${(th*180/Math.PI).toFixed(0)}°</text>
  <!-- Battery -->
  <rect x="${W-106}" y="5" width="102" height="22" rx="6" fill="rgba(0,0,0,.62)"/>
  <rect x="${W-102}" y="9" width="${batW}" height="12" rx="3" fill="rgba(255,255,255,.12)"/>
  <rect x="${W-102}" y="9" width="${(batW*bat/100).toFixed(1)}" height="12" rx="3" fill="${batColor}" opacity=".9"/>
  <rect x="${W-102+batW}" y="11" width="4" height="8" rx="2" fill="rgba(255,255,255,.25)"/>
  <text x="${W-102+batW/2}" y="19" text-anchor="middle" font-size="9" fill="white" font-weight="700" font-family="sans-serif">${bat}%</text>
  <!-- Status badge -->
  <rect x="${(W/2-40).toFixed(0)}" y="${H-22}" width="80" height="19" rx="9" fill="${mc}" opacity=".9"/>
  <text x="${W/2}" y="${H-9}" text-anchor="middle" font-size="10" fill="white" font-weight="800"
        font-family="sans-serif" letter-spacing="1">${ml}</text>
</svg>`;
}

// ── NavimowCard ───────────────────────────────────────────────────────────────
class NavimowCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._cfg = { ...DEFAULTS };
    this._hass = null;
    this._settingsOpen = false;
  }

  static get type() { return 'navimow-card'; }

  static getStubConfig() {
    return { entity_prefix: '', ...DEFAULTS };
  }

  static getConfigElement() {
    return document.createElement('navimow-card-editor');
  }

  setConfig(cfg) {
    if (cfg.entity_prefix === undefined) {
      throw new Error('entity_prefix ist erforderlich (z.B. navimow_m550)');
    }
    this._cfg = { ...DEFAULTS, ...cfg };
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() { return 5; }

  // ── Entity helpers ──────────────────────────────────────────────────────────
  _eid(domain, suffix) {
    const p = this._cfg.entity_prefix;
    return suffix ? `${domain}.${p}_${suffix}` : `${domain}.${p}`;
  }

  _state(domain, suffix) {
    const e = this._hass?.states[this._eid(domain, suffix)];
    return e?.state;
  }

  _attr(domain, suffix, attr) {
    const e = this._hass?.states[this._eid(domain, suffix)];
    return e?.attributes?.[attr];
  }

  _avail(domain, suffix) {
    const s = this._state(domain, suffix);
    return s && s !== 'unavailable' && s !== 'unknown';
  }

  // ── Service calls ───────────────────────────────────────────────────────────
  _svc(domain, service, data) {
    this._hass?.callService(domain, service, data);
  }

  // ── Render ──────────────────────────────────────────────────────────────────
  _render() {
    if (!this._cfg || !this._hass) return;

    const p = this._cfg.entity_prefix;
    if (!p) {
      this._renderUnconfigured();
      return;
    }

    const status  = this._state('sensor', 'status') || this._state('lawn_mower', null) || 'unknown';
    const battery = this._state('sensor', 'battery') || '0';
    const signal  = this._state('sensor', 'signal_strength');
    const posX    = this._state('sensor', 'position_x');
    const posY    = this._state('sensor', 'position_y');
    const posT    = this._state('sensor', 'position_theta');
    const wTime   = this._state('sensor', 'work_time');
    const wArea   = this._state('sensor', 'work_area');
    const errOn   = this._state('binary_sensor', 'error') === 'on';
    const errCode = this._state('sensor', 'error_code');
    const errMsg  = this._state('sensor', 'error_message');
    const edgeSw  = this._state('switch', 'edge_mowing');
    const rainSw  = this._state('switch', 'rain_mode');
    const theftSw = this._state('switch', 'anti_theft');
    const height  = this._state('number', 'cutting_height');

    const haPos   = this._avail('sensor', 'position_x');
    const mowerSt = this._state('lawn_mower', null) || status;

    const mapStates = { x: posX, y: posY, theta: posT, status: mowerSt, battery };
    const mc = STATUS_COLOR[mowerSt] || '#78909C';
    const ml = STATUS_LABEL[mowerSt] || mowerSt.toUpperCase();

    const formatTime = (s) => {
      if (!s || s === 'unavailable' || s === 'unknown') return '—';
      const h = Math.floor(s/3600), m = Math.floor((s%3600)/60);
      return h > 0 ? `${h}h${m}m` : `${m}m`;
    };

    const html = `
      <style>${STYLES}</style>
      <ha-card>

        ${errOn ? `
        <div class="error-bar">
          <ha-icon icon="mdi:alert-circle"></ha-icon>
          <span>Fehler ${errCode ? errCode+': ' : ''}${errMsg || 'Bitte Mäher prüfen'}</span>
        </div>` : ''}

        <div class="header">
          <div class="title">
            <ha-icon icon="mdi:robot-mower"></ha-icon>
            Navimow
          </div>
          <span class="badge" style="background:${mc}">${ml}</span>
        </div>

        ${this._cfg.show_map ? `
        <div class="map-wrap">
          ${haPos
            ? buildMapSVG(mapStates, this._cfg)
            : `<div class="map-offline">
                 <ha-icon icon="mdi:map-marker-off"></ha-icon>
                 <span>Keine Positionsdaten</span>
               </div>`
          }
        </div>` : ''}

        ${this._cfg.show_controls ? `
        <div class="controls">
          <button class="btn ${mowerSt==='mowing'?'act-start':''}" data-action="start">
            <ha-icon icon="mdi:play-circle-outline"></ha-icon>Mähen
          </button>
          <button class="btn ${mowerSt==='paused'?'act-pause':''}" data-action="pause">
            <ha-icon icon="mdi:pause-circle-outline"></ha-icon>Pause
          </button>
          <button class="btn ${mowerSt==='docked'||mowerSt==='charging'?'act-dock':''}" data-action="dock">
            <ha-icon icon="mdi:home-import-outline"></ha-icon>Basis
          </button>
          <button class="btn" data-action="locate">
            <ha-icon icon="mdi:map-marker-radius-outline"></ha-icon>Orten
          </button>
        </div>` : ''}

        ${this._cfg.show_stats ? `
        <div class="divider"></div>
        <div class="stats">
          <div class="stat">
            <ha-icon class="stat-ico" icon="mdi:battery"></ha-icon>
            <span class="stat-val">${battery !== 'unavailable' ? battery+'%' : '—'}</span>
            <span class="stat-lbl">Batterie</span>
          </div>
          <div class="stat">
            <ha-icon class="stat-ico" icon="mdi:timer-outline"></ha-icon>
            <span class="stat-val">${formatTime(wTime)}</span>
            <span class="stat-lbl">Mähzeit</span>
          </div>
          <div class="stat">
            <ha-icon class="stat-ico" icon="mdi:texture-box"></ha-icon>
            <span class="stat-val">${wArea && wArea!=='unavailable' ? Math.round(wArea)+'m²' : '—'}</span>
            <span class="stat-lbl">Fläche</span>
          </div>
        </div>` : ''}

        ${this._cfg.show_settings ? `
        <div class="divider"></div>
        <div class="sect-label">Einstellungen</div>
        <div class="settings">

          <div class="setting-row">
            <div class="setting-lbl">
              <ha-icon icon="mdi:ruler"></ha-icon>
              Schnitthöhe
            </div>
            <div class="height-ctrl">
              <button class="height-btn" data-action="height-down">−</button>
              <span class="height-val">${height && height!=='unavailable' ? Math.round(height)+' mm' : '—'}</span>
              <button class="height-btn" data-action="height-up">+</button>
            </div>
          </div>

          <div class="setting-row">
            <div class="setting-lbl">
              <ha-icon icon="mdi:border-outside"></ha-icon>
              Kantenmähen
            </div>
            <ha-switch
              .checked="${edgeSw === 'on'}"
              data-action="toggle-edge"
            ></ha-switch>
          </div>

          <div class="setting-row">
            <div class="setting-lbl">
              <ha-icon icon="mdi:weather-rainy"></ha-icon>
              Regenmodus
            </div>
            <ha-switch
              .checked="${rainSw === 'on'}"
              data-action="toggle-rain"
            ></ha-switch>
          </div>

          <div class="setting-row">
            <div class="setting-lbl">
              <ha-icon icon="mdi:shield-lock-outline"></ha-icon>
              Diebstahlschutz
            </div>
            <ha-switch
              .checked="${theftSw === 'on'}"
              data-action="toggle-theft"
            ></ha-switch>
          </div>

        </div>` : ''}

      </ha-card>`;

    this.shadowRoot.innerHTML = html;
    this._bindEvents();
  }

  _renderUnconfigured() {
    this.shadowRoot.innerHTML = `
      <style>${STYLES}</style>
      <ha-card>
        <div class="unconfigured">
          <ha-icon icon="mdi:robot-mower-outline"></ha-icon>
          <div class="unc-title">Navimow-Karte nicht konfiguriert</div>
          <div class="unc-hint">Klicke auf Bearbeiten und gib den Entitätspräfix ein<br>
            z.B. <strong>navimow_m550</strong><br>
            (aus sensor.navimow_m550_battery → navimow_m550)</div>
        </div>
      </ha-card>`;
  }

  // ── Event binding ────────────────────────────────────────────────────────────
  _bindEvents() {
    const root = this.shadowRoot;
    const p = this._cfg.entity_prefix;

    // Control buttons
    root.querySelectorAll('button[data-action]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const a = e.currentTarget.dataset.action;
        const lm = this._eid('lawn_mower', null);

        if (a === 'start')  this._svc('lawn_mower', 'start_mowing', { entity_id: lm });
        if (a === 'pause')  this._svc('lawn_mower', 'pause', { entity_id: lm });
        if (a === 'dock')   this._svc('lawn_mower', 'dock', { entity_id: lm });
        if (a === 'locate') this._svc('button', 'press', { entity_id: this._eid('button', 'locate') });
        if (a === 'restart') this._svc('button', 'press', { entity_id: this._eid('button', 'restart') });

        // Cutting height
        if (a === 'height-down' || a === 'height-up') {
          const cur = parseFloat(this._state('number', 'cutting_height')) || 40;
          const step = 5;
          const next = a === 'height-up' ? Math.min(80, cur+step) : Math.max(25, cur-step);
          this._svc('number', 'set_value', { entity_id: this._eid('number', 'cutting_height'), value: next });
        }
      });
    });

    // ha-switch toggles (fires 'change' event)
    root.querySelectorAll('ha-switch[data-action]').forEach(sw => {
      sw.addEventListener('change', (e) => {
        const a = e.currentTarget.dataset.action;
        const on = e.detail?.value ?? e.target.checked;
        const svc = on ? 'turn_on' : 'turn_off';

        if (a === 'toggle-edge')  this._svc('switch', svc, { entity_id: this._eid('switch', 'edge_mowing') });
        if (a === 'toggle-rain')  this._svc('switch', svc, { entity_id: this._eid('switch', 'rain_mode') });
        if (a === 'toggle-theft') this._svc('switch', svc, { entity_id: this._eid('switch', 'anti_theft') });
      });
    });
  }
}

// ── NavimowCardEditor ─────────────────────────────────────────────────────────
class NavimowCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._cfg  = { ...DEFAULTS };
    this._hass = null;
    this._form = null;
  }

  setConfig(cfg) {
    this._cfg = { ...DEFAULTS, ...cfg };
    if (this._form) {
      this._form.data = this._cfg;
    }
  }

  set hass(hass) {
    this._hass = hass;
    if (this._form) this._form.hass = hass;
  }

  connectedCallback() {
    this._build();
  }

  _build() {
    if (this._form) return;

    const style = document.createElement('style');
    style.textContent = `
      ha-form { display: block; padding: 4px 0; }
      .hint { font-size: 11px; color: var(--secondary-text-color);
              padding: 0 16px 10px; line-height: 1.5; }
      code { background: var(--code-editor-background-color, rgba(0,0,0,0.1));
             padding: 1px 5px; border-radius: 4px; font-size: 12px; }
    `;
    this.shadowRoot.appendChild(style);

    const hint = document.createElement('div');
    hint.className = 'hint';
    hint.innerHTML = `
      Gib den <b>Entitätspräfix</b> ein: der Teil vor dem ersten Suffix in deinen Sensor-IDs.<br>
      Beispiel: <code>sensor.navimow_m550_battery</code> → Präfix: <code>navimow_m550</code><br>
      <b>Tipp:</b> Entwicklerwerkzeuge → Zustände → nach <code>navimow</code> suchen.
    `;
    this.shadowRoot.appendChild(hint);

    const form = document.createElement('ha-form');
    form.hass   = this._hass;
    form.data   = this._cfg;
    form.schema = EDITOR_SCHEMA;
    form.computeLabel  = (s) => s.label  || s.name;
    form.computeHelper = (s) => s.description || '';

    form.addEventListener('value-changed', (e) => {
      this._cfg = e.detail.value;
      this.dispatchEvent(new CustomEvent('config-changed', {
        detail: { config: this._cfg },
        bubbles: true,
        composed: true,
      }));
    });

    this._form = form;
    this.shadowRoot.appendChild(form);
  }
}

// ── Registration ──────────────────────────────────────────────────────────────
if (!customElements.get('navimow-card')) {
  customElements.define('navimow-card', NavimowCard);
}
if (!customElements.get('navimow-card-editor')) {
  customElements.define('navimow-card-editor', NavimowCardEditor);
}

window.customCards = window.customCards || [];
if (!window.customCards.find(c => c.type === 'navimow-card')) {
  window.customCards.push({
    type:             'navimow-card',
    name:             'Navimow Mäher-Karte',
    description:      'Live-Karte und Steuerung für Navimow Rasenmäher. Automatisch durch die Integration eingebunden.',
    preview:          true,
    documentationURL: 'https://github.com/daMustermann/NavimowHA',
  });
}

console.info(
  `%c NAVIMOW-CARD %c v${NAVIMOW_CARD_VERSION} `,
  'color:#fff;background:#2e7d32;font-weight:700;padding:2px 4px;border-radius:4px 0 0 4px',
  'color:#2e7d32;background:rgba(46,125,50,.15);font-weight:600;padding:2px 4px;border-radius:0 4px 4px 0',
);
