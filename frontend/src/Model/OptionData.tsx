export type OptionItem = {
    key: string;
    symbol: string;
}

export type OptionGreeksData = {
    delta: number;
    gamma: number;
    vega: number;
    theta: number;
    vanna_vs: number;
    vanna_sv: number;

};

export type WingModelData = {
    atm_vol: number;
    v: number;
    k1: number;
    k2: number;
    b: number;
    atm_available: number
}

export type StrikePrices = {
    call_option: OptionGreeksData;
    put_option: OptionGreeksData;
}

export type GreeksResponse = {
    symbol: string;
    strike_prices: { [key: string]: StrikePrices };
}

