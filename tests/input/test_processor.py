from pireaderos.input.processor import TouchProcessor, TouchPoint, TouchEvent


class TestTouchProcessorInitialization:
    def test_init_is_working_unittest(self):
        processor = TouchProcessor()
        isinstance(processor._last_touch, dict)
        isinstance(processor._is_touching, dict)


class TestTouchProcessorProcessRawTouches:
    def test_process_calls_helpers_unittest(self, mocker):
        MockLift = mocker.patch.object(
            TouchProcessor, "_process_lifted_fingers", return_value=[])
        MockTouch = mocker.patch.object(
            TouchProcessor, "_process_touch_point", return_value=[])

        processor = TouchProcessor()
        processor.process_raw_touches([(0, 12, 12)])

        MockLift.assert_called_once()
        MockTouch.assert_called_once()

    def test_process_returns_events_integration(self):
        touch_sequence = [
            [(0, 1, 1)],  # Down
            [(0, 10, 10)],  # Contact
            [],  # Up
            [(0, 1, 1)],  # Down
            [(0, 10, 10), (1, 10, 10)],  # Contact, Down
            []  # Up, Up
        ]

        processor = TouchProcessor()
        result: list[TouchEvent] = []
        for touches in touch_sequence:
            events = processor.process_raw_touches(touches)
            result.extend(events)

        # Expected result: [
        #     TouchEvent(TouchEventType.DOWN, TouchPoint(0, 1, 1, *)),
        #     TouchEvent(TouchEventType.CONTACT, TouchPoint(0, 10, 10, *)),
        #     TouchEvent(TouchEventType.UP, TouchPoint(0, 10, 10, *)),
        #     TouchEvent(TouchEventType.DOWN, TouchPoint(0, 1, 1, *)),
        #     TouchEvent(TouchEventType.CONTACT, TouchPoint(0, 10, 10, *)),
        #     TouchEvent(TouchEventType.DOWN, TouchPoint(1, 10, 10, *)),
        #     TouchEvent(TouchEventType.UP, TouchPoint(0, 10, 10, *)),
        #     TouchEvent(TouchEventType.UP, TouchPoint(1, 10, 10, *))
        # ]

        assert len(result) == 8

        pt = result[0].point
        assert result[0].type.name == "DOWN"
        assert (pt.id, pt.x, pt.y) == (0, 1, 1)
        pt = result[1].point
        assert result[1].type.name == "CONTACT"
        assert (pt.id, pt.x, pt.y) == (0, 10, 10)
        pt = result[2].point
        assert result[2].type.name == "UP"
        assert (pt.id, pt.x, pt.y) == (0, 10, 10)
        pt = result[3].point
        assert result[3].type.name == "DOWN"
        assert (pt.id, pt.x, pt.y) == (0, 1, 1)
        pt = result[4].point
        assert result[4].type.name == "CONTACT"
        assert (pt.id, pt.x, pt.y) == (0, 10, 10)
        pt = result[5].point
        assert result[5].type.name == "DOWN"
        assert (pt.id, pt.x, pt.y) == (1, 10, 10)
        pt = result[6].point
        assert result[6].type.name == "UP"
        assert (pt.id, pt.x, pt.y) == (0, 10, 10)
        pt = result[7].point
        assert result[7].type.name == "UP"
        assert (pt.id, pt.x, pt.y) == (1, 10, 10)


class TestTouchProcessorProcessLiftedFingers:
    def test_process_returns_empty_list_when_no_finger_lifted_singletouch_unittest(self):
        processor = TouchProcessor()
        processor._last_touch = {0: TouchPoint(0, 1, 1, 1)}
        processor._is_touching = {0: True}

        result = processor._process_lifted_fingers([(0, 2, 2)])

        assert result == []

    def test_process_returns_empty_list_when_no_finger_lifted_multitouch_unittest(self):
        processor = TouchProcessor()
        processor._last_touch = {
            0: TouchPoint(0, 1, 1, 1),
            1: TouchPoint(1, 1, 1, 1)
        }
        processor._is_touching = {0: True, 1: True}

        result = processor._process_lifted_fingers([
            (0, 2, 2), (1, 2, 2)
        ])

        assert result == []

    def test_process_returns_up_event_when_one_finger_lifts_singletouch_unittest(self):
        processor = TouchProcessor()
        processor._last_touch = {0: TouchPoint(0, 1, 1, 1)}
        processor._is_touching = {0: True}

        result = processor._process_lifted_fingers([])

        assert len(result) == 1
        assert result[0].type.name == "UP"
        assert result[0].point == TouchPoint(0, 1, 1, 1)

    def test_process_returns_up_event_when_one_finger_lifts_multitouch_unittest(self):
        processor = TouchProcessor()
        processor._last_touch = {
            0: TouchPoint(0, 1, 1, 1),
            1: TouchPoint(1, 1, 1, 1)
        }
        processor._is_touching = {0: True, 1: True}

        result = processor._process_lifted_fingers([(1, 2, 2)])

        assert len(result) == 1
        assert result[0].type.name == "UP"
        assert result[0].point == TouchPoint(0, 1, 1, 1)

    def test_process_returns_up_event_when_multiple_fingers_lift_multitouch_unittest(self):
        processor = TouchProcessor()
        processor._last_touch = {
            0: TouchPoint(0, 1, 1, 1),
            1: TouchPoint(1, 2, 2, 1)
        }
        processor._is_touching = {0: True, 1: True}

        result = processor._process_lifted_fingers([])

        assert len(result) == 2
        assert result[0].type.name == "UP"
        assert result[0].point == TouchPoint(0, 1, 1, 1)
        assert result[1].type.name == "UP"
        assert result[1].point == TouchPoint(1, 2, 2, 1)


class TestTouchProcessorProcessTouchPoint:
    def test_process_returns_down_event_singletouch_unittest(self):
        processor = TouchProcessor()

        result = processor._process_touch_point(0, TouchPoint(0, 1, 1, 1))

        assert len(result) == 1
        assert result[0].type.name == "DOWN"
        assert result[0].point == TouchPoint(0, 1, 1, 1)

    def test_process_returns_down_event_multitouch_unittest(self):
        processor = TouchProcessor()
        processor._last_touch = {1: TouchPoint(1, 1, 1, 1)}
        processor._is_touching = {1: True}

        result = processor._process_touch_point(0, TouchPoint(0, 1, 1, 1))

        assert len(result) == 1
        assert result[0].type.name == "DOWN"
        assert result[0].point == TouchPoint(0, 1, 1, 1)

    def test_process_returns_contact_event_singletouch_unittest(self):
        processor = TouchProcessor()
        processor._last_touch = {0: TouchPoint(0, 1, 1, 1)}
        processor._is_touching = {0: True}

        result = processor._process_touch_point(0, TouchPoint(0, 1, 1, 1))

        assert len(result) == 1
        assert result[0].type.name == "CONTACT"
        assert result[0].point == TouchPoint(0, 1, 1, 1)

    def test_process_returns_contact_event_multitouch_unittest(self):
        processor = TouchProcessor()
        processor._last_touch = {
            0: TouchPoint(0, 1, 1, 1),
            1: TouchPoint(1, 1, 1, 1)
        }
        processor._is_touching = {0: True, 1: True}

        result = processor._process_touch_point(0, TouchPoint(0, 1, 1, 1))

        assert len(result) == 1
        assert result[0].type.name == "CONTACT"
        assert result[0].point == TouchPoint(0, 1, 1, 1)
