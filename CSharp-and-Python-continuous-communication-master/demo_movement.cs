using UnityEngine;

public class demo_movement : MonoBehaviour
{
    [SerializeField] float movespeed = 60f;
    [SerializeField] float turnspeed = 20f;

    public Communication_py communication_Py;

    void Update()
    {
        Turn();
        Thrust();
    }

    void Turn()
    {
        /*float yaw = Input.GetAxis("Horizontal") * turnspeed * Time.deltaTime;
        float pitch = Input.GetAxis("Pitch") * turnspeed * Time.deltaTime;
        float roll = Input.GetAxis("Roll") * turnspeed * Time.deltaTime;*/


        Vector3 rotate = communication_Py.Rotation_Taken(); 

        transform.Rotate(rotate);
    }

    void Thrust()
    {
        if (communication_Py.Number_Taken() == 1)
            transform.position += 1 * transform.forward * movespeed * Time.deltaTime;

    }
}
