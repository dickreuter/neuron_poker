cmake_minimum_required(VERSION 3.15)
project(montecarlo_cpp)

set(CMAKE_CXX_STANDARD 14)

include_directories("C:/Users/dickr/Anaconda3/include" "C:/Users/dickr/git/vcpkg/installed/x64-windows/include" )
link_directories("C:/Users/dickr/Anaconda3/libs")

add_executable(montecarlo_cpp
        Montecarlo.cpp
        Montecarlo.h
        Test.cpp)

TARGET_LINK_LIBRARIES( montecarlo_cpp LINK_PUBLIC ${Boost_LIBRARIES} )