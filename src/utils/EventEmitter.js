/**
 * 事件发射器
 * 简单的发布-订阅模式实现
 */

export class EventEmitter {
  constructor() {
    this._events = new Map();
  }

  /**
   * 订阅事件
   * @param {string} event 
   * @param {function} listener 
   */
  on(event, listener) {
    if (!this._events.has(event)) {
      this._events.set(event, []);
    }
    this._events.get(event).push(listener);
    return () => this.off(event, listener);
  }

  /**
   * 订阅一次性事件
   * @param {string} event 
   * @param {function} listener 
   */
  once(event, listener) {
    const onceWrapper = (...args) => {
      listener(...args);
      this.off(event, onceWrapper);
    };
    return this.on(event, onceWrapper);
  }

  /**
   * 取消订阅
   * @param {string} event 
   * @param {function} listener 
   */
  off(event, listener) {
    const listeners = this._events.get(event);
    if (listeners) {
      const index = listeners.indexOf(listener);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  /**
   * 发射事件
   * @param {string} event 
   * @param  {...any} args 
   */
  emit(event, ...args) {
    const listeners = this._events.get(event);
    if (listeners) {
      listeners.forEach(listener => {
        try {
          listener(...args);
        } catch (error) {
          console.error(`Error in event listener for "${event}":`, error);
        }
      });
    }
  }

  /**
   * 移除所有监听器
   * @param {string} event 
   */
  removeAllListeners(event) {
    if (event) {
      this._events.delete(event);
    } else {
      this._events.clear();
    }
  }
}

