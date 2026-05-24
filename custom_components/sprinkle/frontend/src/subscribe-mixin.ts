import { PropertyValues, ReactiveElement } from 'lit';
import { property } from 'lit/decorators.js';
import { UnsubscribeFunc } from 'home-assistant-js-websocket';
import { HomeAssistant } from './types';

export type Constructor<T = any> = new (...args: any[]) => T;

export const SubscribeMixin = <T extends Constructor<ReactiveElement>>(superClass: T) => {
  class SubscribeClass extends superClass {
    @property({ attribute: false }) public hass?: HomeAssistant;

    private UnsubscribeFuncs?: Array<UnsubscribeFunc | Promise<UnsubscribeFunc>>;

    public connectedCallback() {
      super.connectedCallback();
      this.__checkSubscribed();
    }

    public disconnectedCallback() {
      super.disconnectedCallback();
      if (this.UnsubscribeFuncs) {
        while (this.UnsubscribeFuncs.length) {
          const unsub = this.UnsubscribeFuncs.pop()!;
          if (unsub instanceof Promise) {
            unsub.then(unsubFunc => unsubFunc());
          } else {
            unsub();
          }
        }
        this.UnsubscribeFuncs = undefined;
      }
    }

    protected updated(changedProps: PropertyValues) {
      super.updated(changedProps);
      if (changedProps.has('hass')) {
        this.__checkSubscribed();
      }
    }

    protected hassSubscribe(): Array<UnsubscribeFunc | Promise<UnsubscribeFunc>> {
      return [];
    }

    private __checkSubscribed(): void {
      if (this.UnsubscribeFuncs !== undefined || !((this as unknown) as Element).isConnected || this.hass === undefined) {
        return;
      }
      this.UnsubscribeFuncs = this.hassSubscribe();
    }
  }
  return SubscribeClass;
};