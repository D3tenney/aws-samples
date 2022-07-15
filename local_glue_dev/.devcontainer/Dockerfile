FROM amazon/aws-glue-libs:glue_libs_3.0.0_image_01

ARG USERNAME
ARG USER_UID
ARG USER_GID

# RUN chown ${USERNAME}:root /tmp/spark-events

# Create non-root user
# RUN groupadd -g $USER_GID $USERNAME && useradd -g $USER_GID -m $USERNAME


# ARG ENABLE_NONROOT_DOCKER="true"

#RUN groupadd docker

#RUN usermod -aG docker $USERNAME