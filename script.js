const menu = [
  { id: "1", nama: "Nasi Goreng", harga: 15000, emoji: "🍛" },
  { id: "2", nama: "Mie Goreng", harga: 12000, emoji: "🍜" },
  { id: "3", nama: "Ayam Penyet", harga: 18000, emoji: "🍗" },
  { id: "4", nama: "Es Teh", harga: 4000, emoji: "🧋" },
  { id: "5", nama: "Es Jeruk", harga: 5000, emoji: "🍊" }
];

const cart = {};
const formatRupiah = n => new Intl.NumberFormat("id-ID", {
  style: "currency", currency: "IDR", maximumFractionDigits: 0
}).format(n);

function renderMenu() {
  const el = document.getElementById("daftar-menu");
  el.innerHTML = "";
  menu.forEach(item => {
    const card = document.createElement("article");
    card.className = "menu-card";
    card.innerHTML = `
      <div class="menu-emoji" aria-hidden="true">${item.emoji}</div>
      <h3>${item.nama}</h3>
      <p class="price">${formatRupiah(item.harga)}</p>
      <button class="primary" type="button" data-add="${item.id}">Tambah ke keranjang</button>`;
    el.appendChild(card);
  });
}

function totals() {
  const subtotal = Object.values(cart).reduce((sum, item) => sum + item.harga * item.jumlah, 0);
  const diskon = subtotal >= 50000 ? Math.round(subtotal * 0.10) : 0;
  const biayaLayanan = Math.round((subtotal - diskon) * 0.05);
  return { subtotal, diskon, biayaLayanan, total: subtotal - diskon + biayaLayanan };
}

function renderCart() {
  const el = document.getElementById("keranjang");
  const entries = Object.entries(cart);
  if (!entries.length) {
    el.innerHTML = '<p class="muted">Keranjang masih kosong.</p>';
  } else {
    el.innerHTML = "";
    entries.forEach(([id, item]) => {
      const row = document.createElement("div");
      row.className = "cart-row";
      row.innerHTML = `
        <div><div class="cart-name">${item.nama}</div>
        <div class="muted">${formatRupiah(item.harga)} × ${item.jumlah} = ${formatRupiah(item.harga * item.jumlah)}</div></div>
        <div class="cart-controls">
          <button class="small-btn" data-minus="${id}" aria-label="Kurangi ${item.nama}">−</button>
          <strong>${item.jumlah}</strong>
          <button class="small-btn" data-plus="${id}" aria-label="Tambah ${item.nama}">+</button>
          <button class="small-btn" data-remove="${id}">Hapus</button>
        </div>`;
      el.appendChild(row);
    });
  }
  const t = totals();
  document.getElementById("subtotal").textContent = formatRupiah(t.subtotal);
  document.getElementById("diskon").textContent = "−" + formatRupiah(t.diskon);
  document.getElementById("biaya-layanan").textContent = formatRupiah(t.biayaLayanan);
  document.getElementById("total").textContent = formatRupiah(t.total);
}

function readHistory() {
  try { return JSON.parse(localStorage.getItem("riwayatPesanan") || "[]"); }
  catch { return []; }
}

function renderHistory() {
  const el = document.getElementById("riwayat");
  const history = readHistory();
  if (!history.length) {
    el.innerHTML = '<p class="muted">Belum ada pesanan tersimpan di browser ini.</p>';
    return;
  }
  el.innerHTML = history.slice().reverse().map(order => `
    <div class="history-item">
      <strong>${order.id}</strong> — ${order.nama} (Meja ${order.meja})<br>
      <span class="muted">${order.waktu} · ${order.metode}</span><br>
      Total: <strong>${formatRupiah(order.total)}</strong>
    </div>`).join("");
}

document.addEventListener("click", event => {
  const target = event.target;
  if (target.dataset.add) {
    const item = menu.find(m => m.id === target.dataset.add);
    if (!cart[item.id]) cart[item.id] = { ...item, jumlah: 0 };
    cart[item.id].jumlah++;
    renderCart();
  }
  if (target.dataset.plus) {
    cart[target.dataset.plus].jumlah++;
    renderCart();
  }
  if (target.dataset.minus) {
    const item = cart[target.dataset.minus];
    item.jumlah--;
    if (item.jumlah <= 0) delete cart[target.dataset.minus];
    renderCart();
  }
  if (target.dataset.remove) {
    delete cart[target.dataset.remove];
    renderCart();
  }
});

document.getElementById("checkout").addEventListener("click", () => {
  const nama = document.getElementById("nama-pelanggan").value.trim();
  const meja = document.getElementById("nomor-meja").value.trim();
  const status = document.getElementById("pesan-status");
  const entries = Object.values(cart);

  if (!nama || !meja) {
    status.textContent = "Isi nama pelanggan dan nomor meja terlebih dahulu.";
    return;
  }
  if (!entries.length) {
    status.textContent = "Keranjang masih kosong. Tambahkan menu terlebih dahulu.";
    return;
  }

  const t = totals();
  const order = {
    id: "ORD-" + Date.now(),
    waktu: new Date().toLocaleString("id-ID"),
    nama, meja,
    items: entries.map(item => ({ nama: item.nama, harga: item.harga, jumlah: item.jumlah })),
    subtotal: t.subtotal,
    diskon: t.diskon,
    biayaLayanan: t.biayaLayanan,
    total: t.total,
    metode: document.getElementById("metode-bayar").value,
    status: "Menunggu konfirmasi"
  };

  const history = readHistory();
  history.push(order);
  try {
    localStorage.setItem("riwayatPesanan", JSON.stringify(history));
  } catch {
    status.textContent = "Riwayat tidak dapat disimpan di browser ini.";
    return;
  }

  const receipt = [
    "PESANAN BERHASIL DICATAT (DEMO)",
    "Nomor: " + order.id,
    "Nama: " + nama,
    "Meja: " + meja,
    ...order.items.map(item => `${item.nama} x${item.jumlah}: ${formatRupiah(item.harga * item.jumlah)}`),
    "Subtotal: " + formatRupiah(t.subtotal),
    "Diskon: " + formatRupiah(t.diskon),
    "Biaya layanan: " + formatRupiah(t.biayaLayanan),
    "TOTAL: " + formatRupiah(t.total),
    "Pembayaran: " + order.metode,
    "Catatan: ini demo, pembayaran tidak diproses otomatis."
  ].join("\\n");
  status.innerHTML = "";
  const pre = document.createElement("pre");
  pre.textContent = receipt;
  status.appendChild(pre);

  Object.keys(cart).forEach(key => delete cart[key]);
  renderCart();
  renderHistory();
});

document.getElementById("hapus-riwayat").addEventListener("click", () => {
  if (confirm("Hapus semua riwayat yang tersimpan di browser ini?")) {
    localStorage.removeItem("riwayatPesanan");
    renderHistory();
  }
});

renderMenu();
renderCart();
renderHistory();
