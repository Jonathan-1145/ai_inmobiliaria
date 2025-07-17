export function getHoraActual() {
    const ahora = new Date();
    let h = ahora.getHours();
    const m = String(ahora.getMinutes()).padStart(2, '0');
    const ampm = h >= 12 ? 'p.m.' : 'a.m.';
    h = h % 12 || 12;
    return `${h}:${m} ${ampm}`;
}
