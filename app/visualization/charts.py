import matplotlib.pyplot as plt
import pandas as pd


def plot_risk_distribution(df):
    counts = df["risk_level"].value_counts()

    fig, ax = plt.subplots()
    counts.plot(kind="bar", ax=ax)
    ax.set_title("Heat Risk Distribution")
    ax.set_xlabel("Risk Level")
    ax.set_ylabel("Number of Areas")

    return fig


def plot_temperature_comparison(df):
    fig, ax = plt.subplots()

    ax.hist(df["ST_B10"], bins=20, alpha=0.6, label="Before")
    ax.hist(df["temp_after"], bins=20, alpha=0.6, label="After")

    ax.set_title("Temperature Distribution: Before vs After")
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Frequency")
    ax.legend()

    return fig


def plot_sdg_impact(df):
    impact_counts = df["sdg_impact"].value_counts()

    fig, ax = plt.subplots()
    impact_counts.plot(kind="pie", autopct="%1.1f%%", ax=ax)
    ax.set_title("SDG Impact Assessment")
    ax.set_ylabel("")

    return fig
