(function(){
  'use strict';
  // Simple logger wrapper used by public pages. Honors window.VERITY_DEBUG (true/false).
  const isDebug = typeof window !== 'undefined' && !!window.VERITY_DEBUG;
  const fmt = (...args) => args.map(a => (typeof a === 'object' ? JSON.stringify(a) : a)).join(' ');

  const logger = {
    debug: (...args) => { if (isDebug && console.debug) console.debug(fmt(...args)); },
    info: (...args) => { if (console.info) console.info(fmt(...args)); else console.log(fmt(...args)); },
    warn: (...args) => { if (console.warn) console.warn(fmt(...args)); else console.log(fmt(...args)); },
    error: (...args) => { if (console.error) console.error(fmt(...args)); else console.log(fmt(...args)); }
  };

  window.verityLogger = window.verityLogger || logger;
})();