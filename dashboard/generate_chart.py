import matplotlib.pyplot as plt

def generate_sales_chart():
    values = [120, 230, 180, 310, 280]
    labels = ["Jan", "Feb", "Mar", "Apr", "May"]

    plt.figure()
    plt.plot(labels, values)
    plt.title("Sales Trend")
    plt.savefig("static/report/sales_chart.png", bbox_inches="tight")
    plt.close()

if __name__ == "__main__":
    generate_sales_chart()
