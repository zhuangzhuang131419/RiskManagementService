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

export type CashGreeksResponse = {
    delta: number,
    delta_cash: number,
    gamma_p_cash: number,
    vega_cash: number,
    db_cash: number,
    vanna_vs_cash: number,
    vanna_sv_cash: number,
    charm_cash: number
}
