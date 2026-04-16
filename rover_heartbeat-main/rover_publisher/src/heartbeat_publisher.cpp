#include <chrono>
#include <functional>
#include <memory>
#include <rclcpp/generic_publisher.hpp>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

using namespace std::chrono_literals;

class Heartbeat_Publisher : public rclcpp::Node
{
    public:
        Heartbeat_Publisher() : Node("heartbeat_publisher"), count_(0)
        {
            publisher_ = this->create_publisher<std_msgs::msg::String>("/rover_heartbeat", 10);

            timer_ = this->create_wall_timer(500ms, std::bind(&Heartbeat_Publisher::timer_callback, this));
        }

    private:
        rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
        rclcpp::TimerBase::SharedPtr timer_;
        size_t count_;

        void timer_callback()
        {
            auto message = std_msgs::msg::String();
            message.set__data("Hello from rover: " + std::to_string(count_++));
            RCLCPP_INFO(this->get_logger(), "Publishing '%s'", message.data.c_str());
            publisher_->publish(message);
        }
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<Heartbeat_Publisher>());
    rclcpp::shutdown();
    return 0;
}