#  Copyright (C) 2017 The OSEDev Authors.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
from django.db import models
from channels import Group


class Room(models.Model):
    name = models.CharField(max_length=256, unique=True)
    description = models.TextField()
    users = models.ManyToManyField("user.User", through="RoomParticipant", related_name="rooms")

    class Meta:
        verbose_name = "Room"
        verbose_name_plural = "Rooms"
        ordering = 'name',

    @property
    def group(self):
        return Group("room-%s" % self.id)

    def send(self, sender, text):
        message = Message.objects.create(room=self, text=text, sender=sender)
        self.group.send(message.data)


class RoomParticipant(models.Model):
    room = models.ForeignKey(Room, related_name="participants")
    user = models.ForeignKey("user.User", related_name="room_participation")
    notify = models.BooleanField(default=False)


class Message(models.Model):
    room = models.ForeignKey(Room, related_name="messages", on_delete=models.CASCADE)
    text = models.TextField()
    sender = models.ForeignKey("user.User", related_name="messages", on_delete=models.PROTECT)
    sent = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = '-sent',

    @property
    def data(self):
        return {
            'room': str(self.room_id),
            'sender': self.sender.username,
            'text': self.text
        }
