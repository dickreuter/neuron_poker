cmake_minimum_required(VERSION 3.15)
project(montecarlo_cpp)


set(CMAKE_CXX_STANDARD 14)

find_package(Boost 1.45.0 COMPONENTS Test) 

if(Boost_FOUND)
  include_directories(${Boost_INCLUDE_DIRS} "C:/Users/dickr/Anaconda3/include")
endif()


add_executable(montecarlo_cpp
        Montecarlo.cpp
        Montecarlo.h
        Test.cpp)

TARGET_LINK_LIBRARIES( montecarlo_cpp LINK_PUBLIC ${Boost_LIBRARIES} ${PYTHON_LIBRARY})