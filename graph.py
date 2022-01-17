import pickle
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# with open("mill1.pkl", "rb") as f:
#     res = pickle.load(f)
#     print("\n###MILL###\n",res)
#     for room_name in res:
#         room = res[room_name]
#         plt.plot(room["time"], room["humidity"], label = room_name)
#     plt.title("Humidity")
#     plt.legend()
#     myFmt = mdates.DateFormatter('%H:%M')
#     plt.gca().xaxis.set_major_formatter(myFmt)
#     plt.ylabel("%")
#     plt.show()

# with open("mill1.pkl", "rb") as f:
#     res = pickle.load(f)
#     print("\n###MILL###\n",res)
#     fig, axs = plt.subplots(2,2)
#     parameters = ("currentTemp","humidity","eco2","tvoc")
#     for i, par in enumerate(parameters):
#         for room_name in res:
#             room = res[room_name]
#             axs[i].plot(room["time"],room[par],label=room_name)
#         axs[i].set_title(par)
#     axs[0].legend()
#     # for room_name in res:
#     #     room = res[room_name]
#     #     plt.plot(room["time"], room["humidity"], label = room_name)
#     # plt.title("Humidity")
#     # plt.legend()
#     myFmt = mdates.DateFormatter('%H:%M')
#     plt.gca().xaxis.set_major_formatter(myFmt)
#     plt.ylabel("%")
#     plt.show()
    
with open("mill1.pkl", "rb") as f:
    res = pickle.load(f)
    print("\n###MILL###\n",res)
    fig, axs = plt.subplots(2,2)
    myFmt = mdates.DateFormatter('%H:%M')
    
    for room_name in res:
        room = res[room_name]
        axs[0,0].plot(room["time"],room["currentTemp"],label=room_name)
    axs[0,0].set_title("Temperature")
    axs[0,0].set_ylabel("°C")
    axs[0,0].legend()
    axs[0,0].xaxis.set_major_formatter(myFmt)
    
    for room_name in res:
        room = res[room_name]
        axs[0,1].plot(room["time"],room["humidity"],label=room_name)
    axs[0,1].set_title("Humidity")
    axs[0,1].set_ylabel("%")
    axs[0,1].xaxis.set_major_formatter(myFmt)
    
    for room_name in res:
        room = res[room_name]
        axs[1,0].plot(room["time"],room["eco2"],label=room_name)
    axs[1,0].set_title("ECO2")
    axs[1,0].set_ylabel("ppm")
    axs[1,0].xaxis.set_major_formatter(myFmt)
    
    for room_name in res:
        room = res[room_name]
        axs[1,1].plot(room["time"],room["tvoc"],label=room_name)
    axs[1,1].set_title("TVOC")
    axs[1,1].set_ylabel("ppb")
    axs[1,1].xaxis.set_major_formatter(myFmt)
    
    fig.suptitle("Mill Sensair measurements 09.12.21")
    plt.show()