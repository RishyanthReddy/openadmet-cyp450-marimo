/**
 * EC-3-1-02: BioactivationTracer Client-Side ES6 SVG Component.
 * 
 * Vanilla ES6 SVG molecule viewer for anywidget & Marimo with:
 *   - 2D coordinate rendering (atoms, single/double/triple/aromatic bonds)
 *   - Radial gradient reactivity halos following the strict metadata contract
 *   - Bidirectional Traitlet synchronization (selected atom clicks, hover states)
 *   - Dark/Light responsive design with zero external JavaScript dependencies
 */

function render({ model, el }) {
  // Unique instance ID to isolate SVG gradient defs and ARIA relationships across multiple widgets
  const instanceId = "bat-" + Math.random().toString(36).substring(2, 9);

  // Container DOM
  const container = document.createElement("div");
  container.className = "bat-container";

  // Header element
  const header = document.createElement("div");
  header.className = "bat-header";

  const topBar = document.createElement("div");
  topBar.className = "bat-top-bar";

  const titleEl = document.createElement("span");
  titleEl.className = "bat-title";
  titleEl.textContent = "BioactivationTracer";

  const badgeEl = document.createElement("span");
  badgeEl.className = "bat-badge";

  topBar.appendChild(titleEl);
  topBar.appendChild(badgeEl);

  // Controls (Overlay Mode Toggles)
  const controls = document.createElement("div");
  controls.className = "bat-controls";
  controls.setAttribute("role", "tablist");
  controls.setAttribute("aria-label", "Overlay Modes");

  const modes = [
    { id: "warheads", label: "Warheads" },
    { id: "fukui", label: "Fukui Radicals" },
    { id: "clean", label: "Clean 2D" }
  ];

  let currentMode = model.get("overlay_mode") || "warheads";

  modes.forEach(m => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.setAttribute("role", "tab");
    btn.setAttribute("aria-selected", currentMode === m.id ? "true" : "false");
    btn.setAttribute("data-mode", m.id);
    btn.className = `bat-btn ${currentMode === m.id ? "active" : ""}`;
    btn.textContent = m.label;
    btn.onclick = () => {
      currentMode = m.id;
      model.set("overlay_mode", currentMode);
      model.save_changes();
      controls.querySelectorAll(".bat-btn").forEach(b => {
        b.classList.remove("active");
        b.setAttribute("aria-selected", "false");
      });
      btn.classList.add("active");
      btn.setAttribute("aria-selected", "true");
      renderSVG();
    };
    controls.appendChild(btn);
  });

  header.appendChild(topBar);
  header.appendChild(controls);

  // SVG Wrapper
  const svgWrapper = document.createElement("div");
  svgWrapper.className = "bat-svg-wrapper";

  // Tooltip
  const tooltip = document.createElement("div");
  tooltip.id = `${instanceId}-tooltip`;
  tooltip.className = "bat-tooltip";
  tooltip.setAttribute("role", "tooltip");
  tooltip.setAttribute("aria-hidden", "true");
  svgWrapper.appendChild(tooltip);

  container.appendChild(header);
  container.appendChild(svgWrapper);
  el.appendChild(container);

  // Helper: Populate Tooltip Content
  function showTooltipContent(atom, metadata) {
    tooltip.innerHTML = `
      <div class="bat-tooltip-header">
        Atom ${atom.symbol}<sub>${atom.index}</sub>
        ${atom.in_warhead ? `<span style="color:${atom.halo_color}; float:right;">⚠️ ${atom.warhead_family}</span>` : ""}
      </div>
      <div class="bat-tooltip-row">
        <span class="bat-tooltip-label">Reactivity Score:</span>
        <span class="bat-tooltip-val">${metadata.atom_score.toFixed(3)}</span>
      </div>
      <div class="bat-tooltip-row">
        <span class="bat-tooltip-label">Metric Type:</span>
        <span class="bat-tooltip-val" style="font-size:10px;">${metadata.score_type}</span>
      </div>
      <div class="bat-tooltip-row">
        <span class="bat-tooltip-label">Provenance Source:</span>
        <span class="bat-tooltip-val" style="font-size:10px;">${metadata.score_source}</span>
      </div>
      <div class="bat-tooltip-row">
        <span class="bat-tooltip-label">Normalization:</span>
        <span class="bat-tooltip-val">${metadata.normalization}</span>
      </div>
    `;
    tooltip.style.display = "block";
    tooltip.setAttribute("aria-hidden", "false");
  }

  // Helper: Position Tooltip with Boundary Clamping
  function positionTooltip(clientX, clientY) {
    const rect = svgWrapper.getBoundingClientRect();
    const relX = Math.max(12, Math.min(clientX - rect.left, rect.width - 12));
    const relY = Math.max(12, Math.min(clientY - rect.top, rect.height - 12));
    tooltip.style.left = `${relX}px`;
    tooltip.style.top = `${relY}px`;
  }

  // Helper: Position Tooltip above DOM Element (for Keyboard Focus)
  function positionTooltipAtElement(elem) {
    const elemRect = elem.getBoundingClientRect();
    const rect = svgWrapper.getBoundingClientRect();
    const relX = elemRect.left + elemRect.width / 2 - rect.left;
    const relY = elemRect.top - rect.top;
    const clampedX = Math.max(12, Math.min(relX, rect.width - 12));
    const clampedY = Math.max(12, Math.min(relY, rect.height - 12));
    tooltip.style.left = `${clampedX}px`;
    tooltip.style.top = `${clampedY}px`;
  }

  // SVG Rendering Function
  function renderSVG() {
    const layout = model.get("layout");
    if (!layout || !layout.atoms || !layout.bonds || layout.is_valid === false) {
      const errMsg = layout && layout.error ? layout.error : "No molecular layout loaded.";
      const warnBox = document.createElement("div");
      warnBox.style.cssText = "padding: 24px; color: #b91c1c; font-size: 13px; background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; margin: 12px;";
      
      const strongEl = document.createElement("strong");
      strongEl.textContent = "⚠️ Structure Warning: ";
      warnBox.appendChild(strongEl);
      
      const msgSpan = document.createElement("span");
      msgSpan.textContent = errMsg;
      warnBox.appendChild(msgSpan);
      
      svgWrapper.replaceChildren(warnBox);
      badgeEl.className = "bat-badge warn";
      badgeEl.textContent = "⚠️ Invalid / Fallback";
      return;
    }

    // Update Header Badge
    if (layout.has_bioactivation_alert) {
      badgeEl.className = "bat-badge warn";
      const uniqueAlerts = [...new Set(layout.warhead_alerts.map(a => a.family))];
      const alertText = uniqueAlerts.join(", ");
      badgeEl.textContent = `⚠️ ${alertText}`;
      badgeEl.title = `Structural alert: ${alertText}`;
    } else {
      badgeEl.className = "bat-badge safe";
      badgeEl.textContent = "✅ Clean (No Alert)";
      badgeEl.title = "No structural bioactivation alerts detected";
    }

    // Clear previous SVG (preserve tooltip)
    const existingSvg = svgWrapper.querySelector("svg");
    if (existingSvg) existingSvg.remove();

    const vb = layout.viewBox;
    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute("viewBox", `${vb.min_x} ${vb.min_y} ${vb.width} ${vb.height}`);
    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
    svg.setAttribute("class", "bat-svg");

    // Defs (Gradients for Halos - scoped to instanceId to prevent collisions across widgets)
    const defs = document.createElementNS(svgNS, "defs");
    defs.innerHTML = `
      <radialGradient id="${instanceId}-halo-red" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#ef4444" stop-opacity="0.85"/>
        <stop offset="45%" stop-color="#ef4444" stop-opacity="0.4"/>
        <stop offset="100%" stop-color="#ef4444" stop-opacity="0"/>
      </radialGradient>
      <radialGradient id="${instanceId}-halo-orange" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#f97316" stop-opacity="0.85"/>
        <stop offset="45%" stop-color="#f97316" stop-opacity="0.4"/>
        <stop offset="100%" stop-color="#f97316" stop-opacity="0"/>
      </radialGradient>
      <radialGradient id="${instanceId}-halo-yellow" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#eab308" stop-opacity="0.85"/>
        <stop offset="45%" stop-color="#eab308" stop-opacity="0.4"/>
        <stop offset="100%" stop-color="#eab308" stop-opacity="0"/>
      </radialGradient>
      <radialGradient id="${instanceId}-halo-pink" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#ec4899" stop-opacity="0.85"/>
        <stop offset="45%" stop-color="#ec4899" stop-opacity="0.4"/>
        <stop offset="100%" stop-color="#ec4899" stop-opacity="0"/>
      </radialGradient>
      <radialGradient id="${instanceId}-halo-cyan" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#06b6d4" stop-opacity="0.85"/>
        <stop offset="45%" stop-color="#06b6d4" stop-opacity="0.4"/>
        <stop offset="100%" stop-color="#06b6d4" stop-opacity="0"/>
      </radialGradient>
    `;
    svg.appendChild(defs);

    // Group Layers
    const halosGroup = document.createElementNS(svgNS, "g");
    halosGroup.setAttribute("class", "bat-halos-layer");

    const bondsGroup = document.createElementNS(svgNS, "g");
    bondsGroup.setAttribute("class", "bat-bonds-layer");

    const atomsGroup = document.createElementNS(svgNS, "g");
    atomsGroup.setAttribute("class", "bat-atoms-layer");

    const atomMap = new Map();
    layout.atoms.forEach(a => atomMap.set(a.index, a));

    // Layer 1: Reactivity Halos
    if (currentMode !== "clean") {
      layout.atoms.forEach(atom => {
        let showHalo = false;
        let haloGradient = `url(#${instanceId}-halo-orange)`;
        let radius = 28;

        if (currentMode === "warheads" && atom.in_warhead) {
          showHalo = true;
          if (atom.halo_color === "#ef4444") haloGradient = `url(#${instanceId}-halo-red)`;
          else if (atom.halo_color === "#f97316") haloGradient = `url(#${instanceId}-halo-orange)`;
          else if (atom.halo_color === "#eab308") haloGradient = `url(#${instanceId}-halo-yellow)`;
          else if (atom.halo_color === "#ec4899") haloGradient = `url(#${instanceId}-halo-pink)`;
          else if (atom.halo_color === "#06b6d4") haloGradient = `url(#${instanceId}-halo-cyan)`;
        } else if (currentMode === "fukui" && atom.fukui_radical > 0.05) {
          showHalo = true;
          haloGradient = `url(#${instanceId}-halo-red)`;
          radius = 20 + Math.min(atom.fukui_radical * 35, 30);
        }

        if (showHalo) {
          const haloCircle = document.createElementNS(svgNS, "circle");
          haloCircle.setAttribute("cx", atom.x);
          haloCircle.setAttribute("cy", atom.y);
          haloCircle.setAttribute("r", radius);
          haloCircle.setAttribute("fill", haloGradient);
          haloCircle.setAttribute("class", "bat-halo");
          halosGroup.appendChild(haloCircle);
        }
      });
    }

    // Layer 2: Bonds
    layout.bonds.forEach(bond => {
      const a1 = atomMap.get(bond.begin_atom);
      const a2 = atomMap.get(bond.end_atom);
      if (!a1 || !a2) return;

      const dx = a2.x - a1.x;
      const dy = a2.y - a1.y;
      const dist = Math.hypot(dx, dy);
      if (dist < 1e-4) return;

      const nx = -dy / dist;
      const ny = dx / dist;

      const isWarheadBond = bond.in_warhead && (currentMode === "warheads");
      const bondClass = `bat-bond-line ${bond.is_aromatic ? "bat-bond-aromatic" : ""} ${isWarheadBond ? "bat-bond-warhead" : ""}`;

      const defaultStroke = bond.is_aromatic ? "#64748b" : "#334155";
      const strokeColor = isWarheadBond ? (a1.halo_color || "#f97316") : defaultStroke;
      const strokeW = isWarheadBond ? "3.2" : "2.2";

      if (bond.order === 1.0 || bond.order === 1.5) {
        // Single or Aromatic Bond
        const line = document.createElementNS(svgNS, "line");
        line.setAttribute("x1", a1.x);
        line.setAttribute("y1", a1.y);
        line.setAttribute("x2", a2.x);
        line.setAttribute("y2", a2.y);
        line.setAttribute("class", bondClass);
        line.setAttribute("stroke", strokeColor);
        line.setAttribute("stroke-width", strokeW);
        line.setAttribute("stroke-linecap", "round");
        if (bond.is_aromatic) line.setAttribute("stroke-dasharray", "4, 3");
        bondsGroup.appendChild(line);
      } else if (bond.order === 2.0) {
        // Double Bond
        const offset = 2.4;
        const line1 = document.createElementNS(svgNS, "line");
        line1.setAttribute("x1", a1.x + nx * offset);
        line1.setAttribute("y1", a1.y + ny * offset);
        line1.setAttribute("x2", a2.x + nx * offset);
        line1.setAttribute("y2", a2.y + ny * offset);
        line1.setAttribute("class", bondClass);
        line1.setAttribute("stroke", strokeColor);
        line1.setAttribute("stroke-width", "2.0");
        line1.setAttribute("stroke-linecap", "round");

        const line2 = document.createElementNS(svgNS, "line");
        line2.setAttribute("x1", a1.x - nx * offset);
        line2.setAttribute("y1", a1.y - ny * offset);
        line2.setAttribute("x2", a2.x - nx * offset);
        line2.setAttribute("y2", a2.y - ny * offset);
        line2.setAttribute("class", bondClass);
        line2.setAttribute("stroke", strokeColor);
        line2.setAttribute("stroke-width", "2.0");
        line2.setAttribute("stroke-linecap", "round");

        bondsGroup.appendChild(line1);
        bondsGroup.appendChild(line2);
      } else if (bond.order === 3.0) {
        // Triple Bond
        const offset = 3.5;
        [-offset, 0, offset].forEach(off => {
          const l = document.createElementNS(svgNS, "line");
          l.setAttribute("x1", a1.x + nx * off);
          l.setAttribute("y1", a1.y + ny * off);
          l.setAttribute("x2", a2.x + nx * off);
          l.setAttribute("y2", a2.y + ny * off);
          l.setAttribute("class", bondClass);
          l.setAttribute("stroke", strokeColor);
          l.setAttribute("stroke-width", "1.8");
          l.setAttribute("stroke-linecap", "round");
          bondsGroup.appendChild(l);
        });
      }
    });

    // Layer 3: Atoms
    layout.atoms.forEach(atom => {
      const g = document.createElementNS(svgNS, "g");
      g.setAttribute("class", "bat-atom-group");
      g.setAttribute("transform", `translate(${atom.x}, ${atom.y})`);

      const isCarbon = atom.symbol === "C";
      const circleRadius = isCarbon ? 5.5 : 9.5;

      // Background Disc
      const bgCircle = document.createElementNS(svgNS, "circle");
      bgCircle.setAttribute("r", circleRadius);
      bgCircle.setAttribute("fill", isCarbon ? "var(--bat-atom-stroke)" : "var(--bat-atom-bg)");
      bgCircle.setAttribute("stroke", atom.element_color || "var(--bat-atom-stroke)");
      bgCircle.setAttribute("stroke-width", isCarbon ? "1" : "1.8");
      bgCircle.setAttribute("class", "bat-atom-circle");
      g.appendChild(bgCircle);

      // Element Label (if heteroatom or charged carbon)
      if (!isCarbon || atom.charge !== 0) {
        const text = document.createElementNS(svgNS, "text");
        text.setAttribute("class", "bat-atom-label");
        text.setAttribute("fill", atom.element_color || "var(--bat-text-main)");
        text.textContent = atom.symbol + (atom.charge > 0 ? "+" : atom.charge < 0 ? "-" : "");
        g.appendChild(text);
      }

      // Metadata Contract Payload
      const metadataContract = {
        atom_index: atom.index,
        atom_symbol: atom.symbol,
        formal_charge: atom.charge,
        is_aromatic: atom.is_aromatic,
        in_warhead: atom.in_warhead,
        warhead_family: atom.warhead_family || "None",
        atom_score: atom.fukui_radical > 0 ? atom.fukui_radical : (atom.in_warhead ? atom.halo_intensity : 0.0),
        score_type: atom.fukui_radical > 0 ? "AIMNet2 Radical Fukui Index (f_k^0)" : (atom.in_warhead ? "Bioactivation Alert Motif" : "Baseline Element"),
        score_source: atom.fukui_radical > 0 ? "AIMNet2-NSE Delta-SCF on RTX 4090" : (atom.in_warhead ? "RDKit SMARTS Substructure Alert" : "Topological Graph"),
        normalization: "Unit range [0, 1]",
        is_experimental: false,
      };

      // Accessibility Attributes
      g.setAttribute("tabindex", "0");
      g.setAttribute("role", "button");
      g.setAttribute("aria-describedby", `${instanceId}-tooltip`);
      g.setAttribute("aria-label", `Atom ${atom.symbol} ${atom.index}: Reactivity ${metadataContract.atom_score.toFixed(3)} (${metadataContract.score_type})`);

      // Selected Atom Visual State Ring
      if (model.get("selected_atom_idx") === atom.index) {
        const selRing = document.createElementNS(svgNS, "circle");
        selRing.setAttribute("r", circleRadius + 4.5);
        selRing.setAttribute("fill", "none");
        selRing.setAttribute("stroke", "var(--bat-btn-active, #2563eb)");
        selRing.setAttribute("stroke-width", "2");
        selRing.setAttribute("stroke-dasharray", "3 2");
        selRing.setAttribute("class", "bat-selected-ring");
        g.appendChild(selRing);
      }

      // Hover Interaction: Tooltip Display
      g.onmouseenter = (e) => {
        showTooltipContent(atom, metadataContract);
        positionTooltip(e.clientX, e.clientY);
      };

      g.onmousemove = (e) => {
        positionTooltip(e.clientX, e.clientY);
      };

      g.onmouseleave = () => {
        tooltip.style.display = "none";
        tooltip.setAttribute("aria-hidden", "true");
      };

      // Focus / Keyboard Interaction
      g.onfocus = () => {
        showTooltipContent(atom, metadataContract);
        positionTooltipAtElement(g);
      };

      g.onblur = () => {
        tooltip.style.display = "none";
        tooltip.setAttribute("aria-hidden", "true");
      };

      g.onkeydown = (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          model.set("selected_atom_idx", atom.index);
          model.set("selected_atom_metadata", metadataContract);
          model.save_changes();
          showTooltipContent(atom, metadataContract);
          positionTooltipAtElement(g);
        }
      };

      // Click Interaction: Traitlet Sync
      g.onclick = () => {
        model.set("selected_atom_idx", atom.index);
        model.set("selected_atom_metadata", metadataContract);
        model.save_changes();
      };

      atomsGroup.appendChild(g);
    });

    svg.appendChild(halosGroup);
    svg.appendChild(bondsGroup);
    svg.appendChild(atomsGroup);
    svgWrapper.appendChild(svg);
  }

  // Reactive listeners
  const onLayoutChange = () => renderSVG();
  const onSelectedAtomChange = () => renderSVG();
  const onOverlayModeChange = () => {
    currentMode = model.get("overlay_mode") || "warheads";
    controls.querySelectorAll(".bat-btn").forEach(b => {
      const isActive = b.getAttribute("data-mode") === currentMode;
      b.classList.toggle("active", isActive);
      b.setAttribute("aria-selected", isActive ? "true" : "false");
    });
    renderSVG();
  };

  model.on("change:layout", onLayoutChange);
  model.on("change:selected_atom_idx", onSelectedAtomChange);
  model.on("change:overlay_mode", onOverlayModeChange);

  // Initial render
  renderSVG();

  // Return AnyWidget ESM lifecycle cleanup callback
  return () => {
    if (model && typeof model.off === "function") {
      model.off("change:layout", onLayoutChange);
      model.off("change:selected_atom_idx", onSelectedAtomChange);
      model.off("change:overlay_mode", onOverlayModeChange);
    }
    el.innerHTML = "";
  };
}

export default { render };
export { render };

