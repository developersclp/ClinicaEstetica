import { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';

/**
 * Portal — renders children directly into document.body,
 * escaping any CSS transform/transition containing block.
 */
export default function Portal({ children }) {
  const el = useRef(document.createElement('div'));

  useEffect(() => {
    const node = el.current;
    document.body.appendChild(node);
    return () => {
      document.body.removeChild(node);
    };
  }, []);

  return createPortal(children, el.current);
}
