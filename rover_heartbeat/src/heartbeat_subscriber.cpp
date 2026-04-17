#include <chrono>
#include <functional>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include "std_msgs/msg/bool.hpp" // Added for the boolean signal

using namespace std::chrono_literals;

class Heartbeat_Subscriber : public rclcpp::Node
{
public:
    Heartbeat_Subscriber() : Node("heartbeat_subscriber")
    {
        this->last_time_ = this->now();

        // Initialize the publisher for the stop signal
        stop_publisher_ = this->create_publisher<std_msgs::msg::Bool>("/rover/stop_signal", 10);

        auto topic_callback = [this](std_msgs::msg::String::SharedPtr msg) -> void
        {
            RCLCPP_INFO(this->get_logger(), "I heard: '%s'", msg->data.c_str());
            this->last_time_ = this->now();
            
            this->publish_stop_signal(false);
        };

        subscription_ = this->create_subscription<std_msgs::msg::String>(
            "/base_station_heartbeat", 10, topic_callback);

        timer_ = this->create_wall_timer(
            100ms, std::bind(&Heartbeat_Subscriber::check_timeout, this));
    }

private:
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
    rclcpp::Publisher<std_msgs::msg::Bool>::SharedPtr stop_publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Time last_time_;

    void publish_stop_signal(bool should_stop)
    {
        auto stop_msg = std_msgs::msg::Bool();
        stop_msg.data = should_stop;
        stop_publisher_->publish(stop_msg);
    }

    void check_timeout()
    {
        auto current_time = this->now();
        auto duration = current_time - last_time_;
        auto max_duration = 2s;

        if (duration > max_duration)
        {
            RCLCPP_WARN(this->get_logger(), "Timeout! Base station lost. Sending STOP signal.");
            publish_stop_signal(true);
        }
    }
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<Heartbeat_Subscriber>());
    rclcpp::shutdown();
    return 0;
}