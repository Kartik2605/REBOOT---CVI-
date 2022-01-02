using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;
using System.Threading;

public class Communication_py : MonoBehaviour
{
    Thread mThread;
    public string connectionIP = "127.0.0.1";
    public int connectionPort = 25001;
    IPAddress localAdd;
    TcpListener listener;
    TcpClient client;

    bool running;
    Vector3 rotation_result;
    int Number;
    string fps;

    public static Vector3 beta0 = new Vector3(0,0,0);

    public static Vector3 beta1 = new Vector3(0,0,0);

    public static float mbar=0f;

    public static float c=0f;
    public static float alpha = 0.7f;

    private void Start()
    {
        ThreadStart ts = new ThreadStart(GetInfo);
        mThread = new Thread(ts);
        mThread.Start();
    }

    private void Update()
    {
        if (c < mbar) 
        {
            rotation_result = ((beta0 - beta1) / mbar) * c + beta1;
        }
        c = c + 1;
    }

    void GetInfo()
    {
        localAdd = IPAddress.Parse(connectionIP);
        listener = new TcpListener(IPAddress.Any, connectionPort);
        listener.Start();

        client = listener.AcceptTcpClient();

        running = true;
        while (running)
        {
            SendAndReceiveData();
        }
        listener.Stop();
    }

    void SendAndReceiveData()
    {
        NetworkStream nwStream = client.GetStream();
        byte[] buffer = new byte[client.ReceiveBufferSize];

        //---receiving Data from the Host----
        int bytesRead = nwStream.Read(buffer, 0, client.ReceiveBufferSize); //Getting data in Bytes from Python
        string dataReceived = Encoding.UTF8.GetString(buffer, 0, bytesRead); //Converting byte data to string
        Debug.Log(dataReceived.Length);
        if (dataReceived.Length > 0)
        {
            Debug.Log(dataReceived);
            string[] data = dataReceived.Split(',');
            string string_roll = data[0];
            string string_pitch = data[1];
            string string_yaw = data[2];
            string number = data[3];
            fps = data[4];
            Number = int.Parse(number);

            beta1 = rotation_result;
            beta0 = new Vector3(float.Parse(string_pitch), float.Parse(string_yaw), float.Parse(string_roll));
            mbar = c * alpha + (1 - alpha) * mbar;
            c = 0;
        }

        /*if (dataReceived != null)
        {
            //---Sending Data to Host----
            byte[] myWriteBuffer = Encoding.ASCII.GetBytes("Hey I got your message Python! Do You see this massage?"); //Converting string to byte data
            nwStream.Write(myWriteBuffer, 0, myWriteBuffer.Length); //Sending the data in Bytes to Python
        }*/
    }


    public Vector3 Rotation_Taken()
    {
        return rotation_result ;
    }

    public int Number_Taken()
    {
        return Number;
    }

    public string FPS_Taken()
    {
        return fps;
    }

    
}