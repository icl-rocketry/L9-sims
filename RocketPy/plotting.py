import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('flight_quali_curve.csv')

df_filtered = df[(df['time'] >= 1829) & (df['time'] <= 1836)]
df_filtered['normalized_time'] = df_filtered['time'] - 1829

plt.figure(figsize=(10, 6))
plt.plot(df_filtered['normalized_time'], df_filtered['thrust'])

plt.title('Flight Qualification Curve (Normalized Time)')
plt.xlabel('Normalized Time (s)')
plt.ylabel('Thrust (N)')

plt.xlim(0, 7)

plt.grid(True)
plt.show()

df_filtered[['normalized_time', 'thrust']].to_csv('normalized_flight_quali_curve.txt', index=False, sep='\t')
