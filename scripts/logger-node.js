const isDebug = !!process.env.VERITY_DEBUG;
function fmt(...args) { return args.map(a => (typeof a === 'object' ? JSON.stringify(a) : a)).join(' '); }
module.exports = {
  debug: (...args) => { if (isDebug) console.debug(fmt(...args)); },
  info: (...args) => console.info(fmt(...args)),
  warn: (...args) => console.warn(fmt(...args)),
  error: (...args) => console.error(fmt(...args))
};