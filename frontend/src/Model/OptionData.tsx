export type OptionItem = {
    key: string;
    symbol: string;
}

export type OptionGreeksData = {
    delta: number;
    gamma: number;
    vega: number;
    theta: number;
};

export type StrikePrices = {
    call_option: OptionGreeksData;
    put_option: OptionGreeksData;
}

export type GreeksResponse = {
    symbol: string;
    strike_prices: { [key: string]: StrikePrices };
}